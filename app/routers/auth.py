from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.dependencies import require_admin
from app.main import limiter
from app.models.refresh_token import RefreshToken
from app.core.security import create_refresh_token, refresh_token_expires
from app.core.config import settings
from app.core.security import oauth2_scheme
from app.db import get_db
from app.schemas.token import TokenPayload, RefreshTokenRequest
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import get_password_hash
from app.core.security import verify_password, create_access_token
from app.db import get_db
from app.models.user import User
from app.schemas.token import Token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(subject=user.email,role=user.role)

    refresh_token_value = create_refresh_token()

    refresh_token = RefreshToken(
        token=refresh_token_value,
        user_id=user.id,
        expires_at=refresh_token_expires(),
    )

    db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer",
    }

@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role="user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user




@router.post("/refresh", response_model=Token)
def refresh_access_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    token_db = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == data.refresh_token,
        )
        .first()
    )

    # token not found -> invalid
    if not token_db:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # already used/revoked -> one-time use
    if token_db.is_revoked:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # expired
    if token_db.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # ROTATION:
    # 1) revoke old refresh token
    token_db.is_revoked = True

    # 2) create new refresh token for same user
    new_refresh_value = create_refresh_token()
    new_refresh = RefreshToken(
        token=new_refresh_value,
        user_id=token_db.user_id,
        expires_at=refresh_token_expires(),
        is_revoked=False,
    )
    db.add(new_refresh)

    # 3) create new access token
    access_token = create_access_token(
        subject=token_db.user.email,
        role=token_db.user.role,
    )
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_value,
        "token_type": "bearer",
    }

@router.post("/logout")
def logout(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    token_db = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token
    ).first()

    if token_db:
        token_db.is_revoked = True
        db.commit()

    return {"message": "Logged out"}