from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.ai_assistant import AssistantRequest

def get_ai_recommendation(
    data: AssistantRequest,
    current_user: User,
    db: Session,
):
    # TEMP response – da endpoint dela
    return {
        "message": "AI assistant connected",
        "user": current_user.email,
        "goal": data.goal,
        "days_per_week": data.days_per_week,
    }