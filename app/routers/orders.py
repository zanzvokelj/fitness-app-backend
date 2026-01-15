
import stripe

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.config import settings
from app.core.dependencies import get_current_user

from app.models.order import Order
from app.models.ticket_plan import TicketPlan


router = APIRouter(
    prefix="/api/v1/orders",
    tags=["orders"],
)
@router.post("/checkout")
def create_checkout(
    plan_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    plan = db.query(TicketPlan).filter(
        TicketPlan.id == plan_id,
        TicketPlan.is_active.is_(True),
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Ticket plan not found")

    order = Order(
        user_id=user.id,
        ticket_plan_id=plan.id,
        price_cents=plan.price_cents,
        currency="EUR",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": plan.name},
                "unit_amount": plan.price_cents,
            },
            "quantity": 1,
        }],
        success_url=settings.FRONTEND_URL + f"/success?order_id={order.id}",
        cancel_url=settings.FRONTEND_URL + "/cancel",
        metadata={"order_id": str(order.id)},
    )

    return {"url": session.url}