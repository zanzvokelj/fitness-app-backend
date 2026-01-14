from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession, joinedload
from datetime import date, datetime, timedelta

from app.db import get_db
from app.models.session import Session
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
        db.query(Session)
        .options(joinedload(Session.class_type))  # 👈 TO JE KLJUČ
        .filter(Session.is_active == True)
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

    return query.order_by(Session.start_time).all()
