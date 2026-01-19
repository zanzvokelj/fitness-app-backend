from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import Request
from app.core.limiter import limiter
from app.db import get_db
from app.models.session import Session as TrainingSession
from app.models.ticket_plan import TicketPlan
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.ai_assistant import AssistantRequest
from app.ai.logic import recommend_sessions
from app.ai.ticket_logic import recommend_ticket
from app.services.ai_fitness_assistant import (
    explain_recommendation,
    explain_recommendation_test,
)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Assistant"])


@router.post("/recommend")
@limiter.limit("5/minute")
def ai_recommendation(
    request: Request,
    data: AssistantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1️⃣ Load data
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

    # 2️⃣ Rule-based recommendations
    recommended_sessions = recommend_sessions(
        goal=data.goal,
        days_per_week=data.days_per_week,
        sessions=sessions,
    )

    ticket = recommend_ticket(
        days_per_week=data.days_per_week,
        plans=plans,
    )

    # 3️⃣ Serialize data for AI
    session_payload = [
        {
            "class": s.class_type.name,
            "date": str(s.start_time.date()),
            "time": s.start_time.strftime("%H:%M"),
        }
        for s in recommended_sessions
    ]

    ticket_payload = (
        {
            "name": ticket.name,
            "price": ticket.price_cents / 100,
        }
        if ticket else None
    )

    # 4️⃣ AI explanation (non-critical layer)
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