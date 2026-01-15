from datetime import datetime, UTC
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.ticket import Ticket
from app.schemas.ticket import TicketOut
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/api/v1/tickets",
    tags=["tickets"],
)

@router.get("/me/active", response_model=TicketOut | None)
def get_active_ticket(
    center_id: int = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    now = datetime.now(UTC)

    return (
        db.query(Ticket)
        .filter(
            Ticket.user_id == user.id,
            Ticket.center_id == center_id,
            Ticket.is_active.is_(True),
            Ticket.valid_from <= now,
            Ticket.valid_until >= now,
        )
        .order_by(
            Ticket.remaining_entries.is_(None),
            Ticket.valid_until.desc(),
        )
        .first()
    )
