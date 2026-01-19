from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.db import get_db
from app.models.session import Session as TrainingSession
from app.models.ticket_plan import TicketPlan
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.ai_assistant import AssistantRequest, AiChatRequest
from app.ai.logic import recommend_sessions
from app.ai.ticket_logic import recommend_ticket
from app.services.ai_chat import chat_with_ai
from app.services.ai_fitness_assistant import (
    explain_recommendation,
    explain_recommendation_test,
)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Assistant"])

WEEKDAYS_SI = [
    "Ponedeljek",
    "Torek",
    "Sreda",
    "Četrtek",
    "Petek",
    "Sobota",
    "Nedelja",
]


@router.post("/recommend")
@limiter.limit("5/minute")
def ai_recommendation(
    request: Request,
    data: AssistantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1️⃣ Load sessions (ignore capacity & dates)
    query = db.query(TrainingSession).filter(
        TrainingSession.is_active.is_(True)
    )

    if data.preferred_center_id:
        query = query.filter(
            TrainingSession.center_id == data.preferred_center_id
        )

    sessions = query.all()

    plans = (
        db.query(TicketPlan)
        .filter(TicketPlan.is_active.is_(True))
        .all()
    )

    # 2️⃣ Rule-based weekly recommendation
    recommended_sessions = recommend_sessions(
        goal=data.goal,
        days_per_week=data.days_per_week,
        sessions=sessions,
    )

    ticket = recommend_ticket(
        days_per_week=data.days_per_week,
        plans=plans,
    )

    # 3️⃣ Serialize weekly plan (NO dates)
    session_payload = [
        {
            "day": WEEKDAYS_SI[s.start_time.weekday()],
            "class": s.class_type.name,
            "time": s.start_time.strftime("%H:%M"),
        }
        for s in recommended_sessions
    ]

    # 4️⃣ Ticket explanation (business logic)
    ticket_payload = None
    if ticket:
        if ticket.max_entries is None:
            ticket_payload = {
                "name": ticket.name,
                "price": ticket.price_cents / 100,
                "reason": (
                    "Če načrtujete redne vadbe skozi vse leto, "
                    "se vam letna karta najbolj izplača. "
                    "V primerjavi z mesečnimi kartami lahko prihranite več kot 200 €."
                ),
            }
        else:
            ticket_payload = {
                "name": ticket.name,
                "price": ticket.price_cents / 100,
                "reason": (
                    "Mesečna karta je optimalna izbira glede na "
                    "vaš trenutni tempo vadbe."
                ),
            }

    # 5️⃣ AI explanation (soft layer)
    ai_explanation = explain_recommendation(
        goal=data.goal,
        days_per_week=data.days_per_week,
        experience_level=data.experience_level,
        sessions=session_payload,
        ticket=ticket_payload,
    )

    return {
        "goal": data.goal,
        "days_per_week": data.days_per_week,
        "recommended_sessions": session_payload,
        "ticket_recommendation": ticket_payload,
        "ai_explanation": ai_explanation,
    }


@router.get("/ai-test")
def ai_test():
    return {"reply": explain_recommendation_test()}


@router.post("/chat")
@limiter.limit("10/minute")
def ai_chat(
    request: Request,
    data: AiChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    messages = [m.model_dump() for m in data.messages]
    reply = chat_with_ai(db, messages)
    return {"reply": reply}