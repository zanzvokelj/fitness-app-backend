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

    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.user_id == user.id,
            Ticket.center_id == center_id,
            Ticket.is_active == True,
            Ticket.valid_from <= now,
            Ticket.valid_until >= now,
        )
        .order_by(Ticket.valid_until.desc())
        .first()
    )

    if not ticket:
        return None

    return {
        "id": ticket.id,
        "type": ticket.plan.code,   # ali ticket.plan.name
        "valid_from": ticket.valid_from,
        "valid_until": ticket.valid_until,
        "is_active": ticket.is_active,
    }