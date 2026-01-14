from datetime import datetime, UTC

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import oauth2_scheme
from app.db import get_db
from app.models.user import User
from app.models.ticket import Ticket


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exception

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def require_active_ticket(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(UTC)

    ticket = db.query(Ticket).filter(
        Ticket.user_id == current_user.id,
        Ticket.is_active.is_(True),
        Ticket.valid_from <= now,
        Ticket.valid_until >= now,
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active ticket",
        )

    return ticket