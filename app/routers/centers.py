from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.db import get_db
from app.models.center import Center
from app.schemas.center import CenterCreate, CenterOut
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/api/v1/centers",
    tags=["centers"],
)


@router.post("/", response_model=CenterOut,status_code=status.HTTP_201_CREATED,)
def create_center(
    data: CenterCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    center = Center(**data.dict())
    db.add(center)
    db.commit()
    db.refresh(center)
    return center


@router.get("/", response_model=list[CenterOut])
def list_centers(
    db: Session = Depends(get_db),
):
    return db.query(Center).filter(Center.is_active == True).all()
