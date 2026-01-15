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

class AdminBookingUserOut(BaseModel):
    email: str

    class Config:
        from_attributes = True


class AdminBookingSessionClassTypeOut(BaseModel):
    name: str

    class Config:
        from_attributes = True


class AdminBookingSessionOut(BaseModel):
    start_time: datetime
    class_type: AdminBookingSessionClassTypeOut

    class Config:
        from_attributes = True


class AdminBookingOut(BaseModel):
    id: int
    status: str
    created_at: datetime

    user: AdminBookingUserOut
    session: AdminBookingSessionOut

    class Config:
        from_attributes = True
