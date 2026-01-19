# app/schemas/ai_assistant.py

from pydantic import BaseModel
from typing import Optional, Literal, List


class AssistantRequest(BaseModel):
    goal: Literal["fat_loss", "strength", "mobility"]
    experience_level: Literal["beginner", "intermediate", "advanced"]
    days_per_week: int
    preferred_center_id: Optional[int] = None


class AiChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AiChatRequest(BaseModel):
    messages: List[AiChatMessage]