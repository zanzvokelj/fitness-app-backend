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
    query = (
        db.query(
            Session,
            func.count(Booking.id).label("booked_count"),
        )
        .outerjoin(
            Booking,
            (Booking.session_id == Session.id)
            & (Booking.status == "active")
        )
        .options(joinedload(Session.class_type))
        .filter(Session.is_active.is_(True))
        .group_by(Session.id)
    )

    if center_id:
        query = query.filter(Session.center_id == center_id)

    if day:
        start = datetime.combine(day, datetime.min.time(), tzinfo=UTC)
        end = start + timedelta(days=1)
        query = query.filter(
            Session.start_time >= start,
            Session.start_time < end,
        )

    results = query.order_by(Session.start_time).all()

    # SQLAlchemy vrne (Session, booked_count) → pretvorimo
    return [
        {
            **session.__dict__,
            "booked_count": booked_count,
        }
        for session, booked_count in results
    ]