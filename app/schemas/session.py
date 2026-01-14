from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.class_type import ClassTypeOut

class SessionCapacityUpdate(BaseModel):
    capacity: int = Field(gt=0)

class SessionBase(BaseModel):
    class_type_id: int
    start_time: datetime
    end_time: datetime
    capacity: int = 10

class SessionCreate(BaseModel):
    center_id: int
    class_type_id: int
    start_time: datetime
    capacity: int


class SessionOut(BaseModel):
    id: int
    center_id: int
    class_type_id: int
    start_time: datetime
    end_time: datetime
    capacity: int
    booked_count: int
    is_active: bool

    class_type: ClassTypeOut

    class Config:
        from_attributes = True

