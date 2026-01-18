from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.dependencies import get_current_user
from app.schemas.ai_assistant import AssistantRequest
from app.models.user import User
from app.services.ai_fitness_assistant import get_ai_recommendation

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["ai"],
)

@router.post("/assistant")
def ai_fitness_assistant(
    data: AssistantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_ai_recommendation(data, current_user, db)