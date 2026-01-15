from datetime import datetime
from pydantic import BaseModel


class PaymentOut(BaseModel):
    id: int
    provider: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True