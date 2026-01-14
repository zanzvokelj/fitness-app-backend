from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.ticket_plan import TicketPlan
from app.schemas.ticket_plan import TicketPlanOut

router = APIRouter(
    prefix="/api/v1/ticket-plans",
    tags=["ticket-plans"],
)


@router.get("/", response_model=list[TicketPlanOut])
def list_ticket_plans(db: Session = Depends(get_db)):
    return (
        db.query(TicketPlan)
        .filter(TicketPlan.is_active == True)
        .order_by(TicketPlan.price_cents)
        .all()
    )