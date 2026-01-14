from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date, UTC

from app.db import get_db
from app.core.dependencies import require_admin
from app.models.session import Session as TrainingSession
from app.models.class_type import ClassType
from app.models.booking import Booking
from app.schemas.session import SessionCreate, SessionOut, SessionCapacityUpdate
from app.schemas.booking import AdminBookingOut
from app.models.user import User
from app.schemas.ticket_plan import TicketPlanOut
from app.schemas.user import AdminUserOut
from app.models.ticket import Ticket
from app.schemas.ticket import AdminTicketOut
from app.schemas.ticket import AdminAssignTicket
from app.models.ticket_plan import TicketPlan

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
)


@router.post("/sessions", response_model=SessionOut)
def create_session(
    data: SessionCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    # enforce timezone-aware datetime
    if data.start_time.tzinfo is None:
        raise HTTPException(
            status_code=400,
            detail="start_time must be timezone-aware (UTC)",
        )

    class_type = db.query(ClassType).filter(
        ClassType.id == data.class_type_id,
        ClassType.is_active.is_(True),
    ).first()

    if not class_type:
        raise HTTPException(status_code=404, detail="Class type not found")

    end_time = data.start_time + timedelta(minutes=class_type.duration)

    session = TrainingSession(
        center_id=data.center_id,
        class_type_id=data.class_type_id,
        start_time=data.start_time,
        end_time=end_time,
        capacity=data.capacity,
        is_active=True,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session



@router.patch("/sessions/{session_id}/capacity", response_model=SessionOut)
def update_session_capacity(
    session_id: int,
    data: SessionCapacityUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    session = db.query(TrainingSession).filter(
        TrainingSession.id == session_id,
        TrainingSession.is_active.is_(True),
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    active_bookings = db.query(func.count(Booking.id)).filter(
        Booking.session_id == session_id,
        Booking.status == "active",
    ).scalar()

    if data.capacity < active_bookings:
        raise HTTPException(
            status_code=400,
            detail=f"Capacity cannot be lower than active bookings ({active_bookings})",
        )

    session.capacity = data.capacity
    db.commit()
    db.refresh(session)

    return session


@router.patch("/sessions/{session_id}/cancel", response_model=SessionOut)
def cancel_session(
    session_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    session = db.query(TrainingSession).filter(
        TrainingSession.id == session_id,
        TrainingSession.is_active.is_(True),
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Active session not found",
        )

    session.is_active = False
    db.commit()
    db.refresh(session)

    return session


@router.get("/bookings", response_model=list[AdminBookingOut])
def view_bookings(
    session_id: int | None = None,
    center_id: int | None = None,
    day: date | None = None,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    query = db.query(Booking).join(TrainingSession)

    if session_id:
        query = query.filter(Booking.session_id == session_id)

    if center_id:
        query = query.filter(TrainingSession.center_id == center_id)

    if day:
        start = datetime(day.year, day.month, day.day, tzinfo=UTC)
        end = start + timedelta(days=1)

        query = query.filter(
            TrainingSession.start_time >= start,
            TrainingSession.start_time < end,
        )

    return query.order_by(Booking.created_at.desc()).all()



@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(
    center_id: int | None = None,
    day: date | None = None,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    query = db.query(TrainingSession).join(ClassType)

    if center_id:
        query = query.filter(TrainingSession.center_id == center_id)

    if day:
        start = datetime(day.year, day.month, day.day, tzinfo=UTC)
        end = start + timedelta(days=1)
        query = query.filter(
            TrainingSession.start_time >= start,
            TrainingSession.start_time < end,
        )

    return query.order_by(TrainingSession.start_time).all()



@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )



@router.get("/tickets", response_model=list[AdminTicketOut])
def list_active_tickets(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    now = datetime.now(UTC)

    return (
        db.query(Ticket)
        .filter(
            Ticket.is_active.is_(True),
            Ticket.valid_until >= now,
        )
        .order_by(Ticket.valid_until)
        .all()
    )


@router.post("/tickets/assign")
def assign_ticket(
    data: AdminAssignTicket,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    plan = db.query(TicketPlan).filter(
        TicketPlan.id == data.plan_id,
        TicketPlan.is_active.is_(True),
    ).first()

    if not plan:
        raise HTTPException(404, "Ticket plan not found")

    now = datetime.now(UTC)

    valid_until = (
        now + timedelta(days=plan.duration_days)
        if plan.duration_days
        else now + timedelta(days=365 * 10)  # “unlimited”
    )

    ticket = Ticket(
        user_id=data.user_id,
        center_id=data.center_id,
        plan_id=data.plan_id,
        valid_from=now,
        valid_until=valid_until,
        is_active=True,
    )

    db.add(ticket)
    db.commit()

    return {"status": "ticket assigned"}



@router.patch("/tickets/{ticket_id}/deactivate")
def deactivate_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.is_active.is_(True),
    ).first()

    if not ticket:
        raise HTTPException(404, "Active ticket not found")

    ticket.is_active = False
    db.commit()

    return {"status": "ticket deactivated"}



@router.get("/users/{user_id}/tickets", response_model=list[AdminTicketOut])
def user_ticket_history(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return (
        db.query(Ticket)
        .filter(Ticket.user_id == user_id)
        .order_by(Ticket.created_at.desc())
        .all()
    )




@router.get("/ticket-plans", response_model=list[TicketPlanOut])
def admin_ticket_plans(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return db.query(TicketPlan).order_by(TicketPlan.price_cents).all()



@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(404, "User not found")

    user.role = role
    db.commit()
    return {"status": "updated"}



@router.patch("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    user = db.query(User).get(user_id)
    user.is_active = False
    db.commit()

