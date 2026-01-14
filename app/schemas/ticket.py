from datetime import datetime
from pydantic import BaseModel

class TicketOut(BaseModel):
    id: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    type: str

    class Config:
        from_attributes = True