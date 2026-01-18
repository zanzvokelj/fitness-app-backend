from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.ai_fitness_assistant import explain_recommendation
from app.db import get_db
from app.models.session import Session as TrainingSession
from app.models.ticket_plan import TicketPlan
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.ai_assistant import AssistantRequest
from app.ai.logic import recommend_sessions
from app.ai.ticket_logic import recommend_ticket

router = APIRouter(prefix="/api/v1/ai", tags=["AI Assistant"])


@router.post("/recommend")
def ai_recommendation(
    data: AssistantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(TrainingSession)
        .filter(TrainingSession.is_active.is_(True))
        .all()
    )

    plans = (
        db.query(TicketPlan)
        .filter(TicketPlan.is_active.is_(True))
        .all()
    )

    recommended_sessions = recommend_sessions(
        goal=data.goal,
        days_per_week=data.days_per_week,
        sessions=sessions,
    )

    ticket = recommend_ticket(
        days_per_week=data.days_per_week,
        plans=plans,
    )


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
            "price": ticket.price,
        }
        if ticket else None
    )

    # AI explanation
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