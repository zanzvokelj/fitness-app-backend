from datetime import datetime
from pydantic import BaseModel
from app.schemas.ticket_plan import TicketPlanOut


class TicketOut(BaseModel):
    id: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    plan: TicketPlanOut

    class Config:
        from_attributes = True

class AdminTicketOut(BaseModel):
    id: int
    user_id: int
    center_id: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool

    plan: TicketPlanOut

    class Config:
        from_attributes = True

class AdminAssignTicket(BaseModel):
    user_id: int
    center_id: int
    plan_id: int