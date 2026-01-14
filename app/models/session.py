from sqlalchemy import DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC

from app.db.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    class_type_id: Mapped[int] = mapped_column(
        ForeignKey("class_types.id", ondelete="CASCADE"),
        nullable=False,
    )

    center_id: Mapped[int] = mapped_column(
        ForeignKey("centers.id", ondelete="CASCADE"),
        nullable=False,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    booked_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # relationships
    class_type = relationship("ClassType")