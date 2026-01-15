from datetime import datetime
from pydantic import BaseModel


class OrderOut(BaseModel):
    id: int
    price_cents: int
    currency: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True