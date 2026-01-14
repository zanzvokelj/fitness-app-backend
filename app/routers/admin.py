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


@router.post("/tickets/seed")
def seed_ticket(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    from app.models.ticket import Ticket

    now = datetime.now(UTC)

    ticket = Ticket(
        user_id=admin.id,
        type="monthly",
        valid_from=now,
        valid_until=now + timedelta(days=30),
        is_active=True,
    )

    db.add(ticket)
    db.commit()

    return {"status": "ticket created"}


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