from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession, joinedload
from sqlalchemy import func
from datetime import date, datetime, timedelta, UTC

from app.db import get_db
from app.models.session import Session
from app.models.booking import Booking
from app.schemas.session import SessionOut

router = APIRouter(
    prefix="/api/v1/sessions",
    tags=["sessions"],
)


@router.get("/", response_model=list[SessionOut])
def list_sessions(
    center_id: int | None = None,
    day: date | None = None,
    db: DBSession = Depends(get_db),
):
    # 🔹 subquery za booked_count
    booked_count_subq = (
        db.query(
            Booking.session_id,
            func.count(Booking.id).label("booked_count"),
        )
        .filter(Booking.status == "active")
        .group_by(Booking.session_id)
        .subquery()
    )

    query = (
        db.query(Session)
        .outerjoin(
            booked_count_subq,
            Session.id == booked_count_subq.c.session_id,
        )
        .options(joinedload(Session.class_type))
        .filter(Session.is_active.is_(True))
    )

    if center_id:
        query = query.filter(Session.center_id == center_id)

    if day:
        start = datetime.combine(day, datetime.min.time())
        end = start + timedelta(days=1)
        query = query.filter(
            Session.start_time >= start,
            Session.start_time < end,
        )

    sessions = query.order_by(Session.start_time).all()

    # 🔹 ročno pripnemo booked_count (ker je subquery)
    for s in sessions:
        s.booked_count = (
            db.query(func.count(Booking.id))
            .filter(
                Booking.session_id == s.id,
                Booking.status == "active",
            )
            .scalar()
        )

    return sessions