import stripe
from fastapi import APIRouter, Request, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.order import Order
from app.models.payment import Payment
from app.models.ticket import Ticket
from app.models.ticket_plan import TicketPlan
from datetime import datetime, UTC, timedelta

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    db: Session = SessionLocal()
    try:
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            order_id = int(session["metadata"]["order_id"])

            order = db.query(Order).get(order_id)
            if not order:
                raise HTTPException(404, "Order not found")

            # 🔒 idempotency check
            existing_payment = db.query(Payment).filter(
                Payment.order_id == order.id
            ).first()
            if existing_payment:
                return {"status": "already processed"}

            # mark order paid
            order.status = "paid"

            payment = Payment(
                order_id=order.id,
                provider="stripe",
                provider_reference=session["id"],
                status="succeeded",
            )
            db.add(payment)

            # 🎟️ CREATE TICKET
            plan = db.query(TicketPlan).get(order.ticket_plan_id)
            if not plan:
                raise HTTPException(500, "Ticket plan missing")

            now = datetime.now(UTC)
            valid_until = (
                now + timedelta(days=plan.duration_days)
                if plan.duration_days
                else now.replace(year=now.year + 10)
            )

            ticket = Ticket(
                user_id=order.user_id,
                center_id=1,  # ali iz plana / future logic
                plan_id=plan.id,
                valid_from=now,
                valid_until=valid_until,
                is_active=True,
            )

            db.add(ticket)
            db.commit()

        return {"status": "ok"}

    finally:
        db.close()