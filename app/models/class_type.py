from sqlalchemy import String, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC

from app.db.base import Base


class ClassType(Base):
    __tablename__ = "class_types"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    center_id: Mapped[int] = mapped_column(
        ForeignKey("centers.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # relationships
    center = relationship("Center")
