from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.ticket_plan import TicketPlan


PLANS = [
    {
        "name": "Mesečna karta",
        "code": "monthly",
        "price_cents": 5000,
        "duration_days": 30,
        "max_entries": None,
    },
    {
        "name": "Letna karta",
        "code": "yearly",
        "price_cents": 40000,
        "duration_days": 365,
        "max_entries": None,
    },
    {
        "name": "10 obiskov",
        "code": "ten-pack",
        "price_cents": 5000,
        "duration_days": None,
        "max_entries": 10,
    },
    {
        "name": "En obisk",
        "code": "single",
        "price_cents": 1000,
        "duration_days": 1,
        "max_entries": 1,
    },
]


def seed():
    db: Session = SessionLocal()

    for plan in PLANS:
        exists = db.query(TicketPlan).filter_by(code=plan["code"]).first()
        if exists:
            continue

        db.add(TicketPlan(**plan))

    db.commit()
    db.close()
    print("Ticket plans seeded")


if __name__ == "__main__":
    seed()