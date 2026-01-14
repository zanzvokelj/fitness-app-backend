from datetime import datetime
from pydantic import BaseModel


class TicketOut(BaseModel):
    id: int
    type: str
    valid_from: datetime
    valid_until: datetime
    is_active: bool

    class Config:
        from_attributes = True
