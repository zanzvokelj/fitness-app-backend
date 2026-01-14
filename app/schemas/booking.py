from pydantic import BaseModel
from datetime import datetime

from app.schemas.session import SessionOut


class BookingOut(BaseModel):
    id: int
    session_id: int
    status: str
    created_at: datetime
    session: SessionOut

    class Config:
        from_attributes = True

class AdminBookingOut(BaseModel):
    id: int
    status: str
    created_at: datetime

    user_id: int
    session_id: int

    class Config:
        from_attributes = True