from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.class_type import ClassType
from app.models.center import Center
from app.schemas.class_type import ClassTypeCreate, ClassTypeOut
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/api/v1/class-types",
    tags=["class-types"],
)


@router.post("/", response_model=ClassTypeOut)
def create_class_type(
    data: ClassTypeCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    center = db.query(Center).filter(Center.id == data.center_id).first()
    if not center:
        raise HTTPException(status_code=404, detail="Center not found")

    class_type = ClassType(**data.dict())
    db.add(class_type)
    db.commit()
    db.refresh(class_type)
    return class_type


@router.get("/", response_model=list[ClassTypeOut])
def list_class_types(
    center_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(ClassType)
    if center_id:
        query = query.filter(ClassType.center_id == center_id)
    return query.all()
