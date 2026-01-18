from pydantic import BaseModel
from typing import Optional

class AssistantRequest(BaseModel):
    goal: str  # e.g. "fat_loss", "strength", "general_fitness"
    experience_level: str  # beginner / intermediate / advanced
    days_per_week: int  # how many times user wants to train
    preferred_center_id: Optional[int] = None