from pydantic import BaseModel


class CenterBase(BaseModel):
    name: str
    address: str
    city: str


class CenterCreate(CenterBase):
    pass


class CenterOut(CenterBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
