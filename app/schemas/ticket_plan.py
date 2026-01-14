from pydantic import BaseModel


class TicketPlanOut(BaseModel):
    id: int
    name: str
    code: str
    price_cents: int
    duration_days: int | None
    max_entries: int | None

    class Config:
        from_attributes = True