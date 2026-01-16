from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime, timedelta, date, UTC
from sqlalchemy.orm import selectinload
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
from app.models.center import Center
from app.schemas.center import CenterCreate, CenterOut
from app.schemas.class_type import ClassTypeCreate, ClassTypeOut
router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
)


@router.get("/me")
def admin_me(admin=Depends(require_admin)):
    return {"is_admin": True}

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
    status: str | None = None,
    email: str | None = None,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    query = (
        db.query(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.session).selectinload(TrainingSession.class_type),
        )
        .join(TrainingSession)
        .join(User)
    )

    if session_id is not None:
        query = query.filter(Booking.session_id == session_id)

    if center_id is not None:
        query = query.filter(TrainingSession.center_id == center_id)

    if status is not None:
        query = query.filter(Booking.status == status)

    if email is not None:
        query = query.filter(User.email.ilike(f"%{email}%"))

    if day is not None:
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

    if center_id is not None:
        query = query.filter(TrainingSession.center_id == center_id)

    if day is not None:
        start = datetime.combine(day, datetime.min.time(), tzinfo=UTC)
        end = start + timedelta(days=1)
        query = query.filter(
            TrainingSession.start_time >= start,
            TrainingSession.start_time < end,
        )

    return query.order_by(TrainingSession.start_time).all()



@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    has_valid_ticket: bool | None = None,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    now = datetime.now(UTC)

    query = db.query(User)

    if has_valid_ticket is not None:
        valid_ticket_subquery = (
            db.query(Ticket.user_id)
            .filter(
                Ticket.is_active.is_(True),
                Ticket.valid_from <= now,
                Ticket.valid_until >= now,
                or_(
                    Ticket.remaining_entries.is_(None),
                    Ticket.remaining_entries > 0,
                ),
            )
            .subquery()
        )

        if has_valid_ticket:
            query = query.filter(User.id.in_(valid_ticket_subquery))
        else:
            query = query.filter(~User.id.in_(valid_ticket_subquery))

    return query.order_by(User.created_at.desc()).all()

@router.get("/tickets", response_model=list[AdminTicketOut])
def list_tickets(
    email: str | None = None,
    plan_id: int | None = None,
    status: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    query = (
        db.query(Ticket)
        .join(User)
        .options(selectinload(Ticket.plan), selectinload(Ticket.user))
    )

    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))

    if plan_id:
        query = query.filter(Ticket.plan_id == plan_id)

    if status == "active":
        query = query.filter(Ticket.is_active.is_(True))
    elif status == "inactive":
        query = query.filter(Ticket.is_active.is_(False))

    if from_date:
        query = query.filter(Ticket.valid_from >= from_date)

    if to_date:
        query = query.filter(Ticket.valid_from <= to_date)

    return query.order_by(Ticket.created_at.desc()).all()

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
        remaining_entries=plan.max_entries,
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



@router.patch("/tickets/{ticket_id}/entries")
def update_ticket_entries(
    ticket_id: int,
    remaining_entries: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    if remaining_entries < 0:
        raise HTTPException(400, "remaining_entries cannot be negative")

    ticket.remaining_entries = remaining_entries
    ticket.is_active = remaining_entries > 0 or ticket.remaining_entries is None

    db.commit()
    return {"status": "updated"}



@router.patch("/tickets/{ticket_id}/validity")
def update_ticket_validity(
    ticket_id: int,
    valid_until: datetime,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    if valid_until <= ticket.valid_from:
        raise HTTPException(400, "valid_until must be after valid_from")

    ticket.valid_until = valid_until
    ticket.is_active = valid_until >= datetime.now(UTC)

    db.commit()
    return {"status": "validity updated"}



@router.get("/centers", response_model=list[CenterOut])
def list_centers(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return db.query(Center).order_by(Center.name).all()


@router.post("/centers", response_model=CenterOut)
def create_center(
    data: CenterCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    center = Center(name=data.name, is_active=True)
    db.add(center)
    db.commit()
    db.refresh(center)
    return center


@router.patch("/centers/{center_id}", response_model=CenterOut)
def update_center(
    center_id: int,
    data: CenterCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    center = db.query(Center).get(center_id)
    if not center:
        raise HTTPException(404, "Center not found")

    center.name = data.name
    db.commit()
    db.refresh(center)
    return center


@router.patch("/centers/{center_id}/deactivate")
def deactivate_center(
    center_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    center = db.query(Center).get(center_id)
    if not center:
        raise HTTPException(404, "Center not found")

    center.is_active = False
    db.commit()
    return {"status": "deactivated"}





@router.get("/class-types", response_model=list[ClassTypeOut])
def list_class_types(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return db.query(ClassType).order_by(ClassType.name).all()


@router.post("/class-types", response_model=ClassTypeOut)
def create_class_type(
    data: ClassTypeCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    ct = ClassType(
        name=data.name,
        duration=data.duration,
        is_active=True,
    )
    db.add(ct)
    db.commit()
    db.refresh(ct)
    return ct


@router.patch("/class-types/{class_type_id}", response_model=ClassTypeOut)
def update_class_type(
    class_type_id: int,
    data: ClassTypeCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    ct = db.query(ClassType).get(class_type_id)
    if not ct:
        raise HTTPException(404, "Class type not found")

    ct.name = data.name
    ct.duration = data.duration
    db.commit()
    db.refresh(ct)
    return ct


@router.patch("/class-types/{class_type_id}/deactivate")
def deactivate_class_type(
    class_type_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    ct = db.query(ClassType).get(class_type_id)
    ct.is_active = False
    db.commit()
    return {"status": "deactivated"}




@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    now = datetime.now(UTC)
    start_month = now.replace(day=1)

    total_users = db.query(func.count(User.id)).scalar()

    users_by_day = (
        db.query(
            func.date(User.created_at).label("day"),
            func.count(User.id).label("count"),
        )
        .group_by(func.date(User.created_at))
        .order_by("day")
        .all()
    )

    active_tickets = (
        db.query(func.count(Ticket.id))
        .filter(
            Ticket.is_active.is_(True),
            Ticket.valid_until >= now,
        )
        .scalar()
    )

    total_bookings = (
        db.query(func.count(Booking.id))
        .filter(Booking.status == "active")
        .scalar()
    )

    bookings_by_weekday = (
        db.query(
            func.extract("dow", TrainingSession.start_time).label("weekday"),
            func.count(Booking.id).label("count"),
        )
        .select_from(Booking)
        .join(TrainingSession, Booking.session_id == TrainingSession.id)
        .filter(Booking.status == "active")
        .group_by("weekday")
        .order_by("weekday")
        .all()
    )

    revenue_this_month = (
        db.query(func.coalesce(func.sum(TicketPlan.price_cents), 0))
        .select_from(Ticket)
        .join(TicketPlan, Ticket.plan_id == TicketPlan.id)
        .filter(Ticket.created_at >= start_month)
        .scalar()
    )

    revenue_by_day = (
        db.query(
            func.date(Ticket.created_at).label("day"),
            func.sum(TicketPlan.price_cents).label("revenue"),
        )
        .select_from(Ticket)
        .join(TicketPlan, Ticket.plan_id == TicketPlan.id)
        .group_by(func.date(Ticket.created_at))
        .order_by("day")
        .all()
    )

    popular_classes = (
        db.query(
            ClassType.name,
            func.count(Booking.id).label("count"),
        )
        .select_from(Booking)
        .join(TrainingSession, Booking.session_id == TrainingSession.id)
        .join(ClassType, TrainingSession.class_type_id == ClassType.id)
        .group_by(ClassType.name)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
        .all()
    )

    return {
        "kpis": {
            "users": total_users,
            "active_tickets": active_tickets,
            "bookings": total_bookings,
            "revenue": revenue_this_month / 100,
        },
        "users_by_day": users_by_day,
        "revenue_by_day": revenue_by_day,
        "bookings_by_weekday": bookings_by_weekday,
        "popular_classes": popular_classes,
    }