# app/ai/ticket_logic.py

from app.models.ticket_plan import TicketPlan


def recommend_ticket(
    *,
    days_per_week: int,
    plans: list[TicketPlan],
):
    monthly_sessions = days_per_week * 4

    # unlimited plans first
    unlimited = [p for p in plans if p.entries is None]
    if unlimited:
        return unlimited[0]

    # otherwise best fitting entries
    for plan in sorted(plans, key=lambda p: p.entries):
        if plan.entries >= monthly_sessions:
            return plan

    return None