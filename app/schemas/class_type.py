from pydantic import BaseModel


class ClassTypeBase(BaseModel):
    name: str
    description: str | None = None
    center_id: int
    duration: int


class ClassTypeCreate(ClassTypeBase):
    pass


class ClassTypeOut(ClassTypeBase):
    id: int

    class Config:
        from_attributes = True
