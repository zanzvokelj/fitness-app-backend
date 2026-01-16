import stripe
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, UTC, timedelta

from app.core.config import settings
from app.db import get_db
from app.models.order import Order
from app.models.payment import Payment
from app.models.ticket import Ticket
from app.models.ticket_plan import TicketPlan

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
    db: Session = Depends(get_db),
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

    if event["type"] != "checkout.session.completed":
        return {"status": "ignored"}

    session = event["data"]["object"]

    if session.get("payment_status") != "paid":
        return {"status": "not paid"}

    order_id = int(session["metadata"]["order_id"])

    order = db.get(Order, order_id)
    if not order:
        return {"status": "order not found"}

    # 🔒 IDEMPOTENCY
    existing_payment = (
        db.query(Payment)
        .filter(Payment.order_id == order.id)
        .first()
    )
    if existing_payment:
        return {"status": "already processed"}

    order.status = "paid"

    payment = Payment(
        order_id=order.id,
        provider="stripe",
        provider_reference=session["id"],
        status="succeeded",
    )
    db.add(payment)

    plan = db.get(TicketPlan, order.ticket_plan_id)
    if not plan:
        return {"status": "plan missing"}

    now = datetime.now(UTC)

    valid_until = (
        now + timedelta(days=plan.duration_days)
        if plan.duration_days
        else now.replace(year=now.year + 10)
    )

    # 🎟️ ENTRY-BASED PLAN → ACCUMULATE
    if plan.max_entries is not None:
        existing_ticket = (
            db.query(Ticket)
            .filter(
                Ticket.user_id == order.user_id,
                Ticket.center_id == 1,  # TODO multi-center
                Ticket.is_active.is_(True),
                Ticket.remaining_entries.isnot(None),
                Ticket.valid_until >= now,
            )
            .order_by(Ticket.valid_until.desc())
            .first()
        )

        if existing_ticket:
            existing_ticket.remaining_entries += plan.max_entries
            existing_ticket.is_active = True
            db.commit()
            return {
                "status": "entries accumulated",
                "added": plan.max_entries,
            }

    # 🆕 CREATE NEW TICKET
    ticket = Ticket(
        user_id=order.user_id,
        center_id=1,
        plan_id=plan.id,
        valid_from=now,
        valid_until=valid_until,
        remaining_entries=plan.max_entries,
        is_active=True,
    )

    db.add(ticket)
    db.commit()

    return {"status": "ticket created"}