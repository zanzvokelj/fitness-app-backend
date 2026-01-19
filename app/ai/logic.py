# app/ai/ticket_logic.py

from app.models.ticket_plan import TicketPlan


def recommend_ticket(
    *,
    days_per_week: int,
    plans: list[TicketPlan],
) -> TicketPlan | None:
    """
    Recommend the most suitable ticket plan based on
    desired training frequency.

    Logic:
    - Prefer unlimited plans
    - Otherwise choose the smallest plan that covers monthly usage
    """

    monthly_sessions = days_per_week * 4

    # 1️⃣ Unlimited plans first
    unlimited = [
        p for p in plans
        if p.is_active and p.max_entries is None
    ]
    if unlimited:
        return unlimited[0]

    # 2️⃣ Limited plans that fit usage
    suitable = [
        p for p in plans
        if p.is_active
        and p.max_entries is not None
        and p.max_entries >= monthly_sessions
    ]

    if suitable:
        return min(suitable, key=lambda p: p.max_entries)

    return None