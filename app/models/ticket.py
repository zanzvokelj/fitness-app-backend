from sqlalchemy import ForeignKey, DateTime, String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from app.models.ticket_plan import TicketPlan
from app.db.base import Base
from app.models.user import User
from app.models.center import Center

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    center_id: Mapped[int] = mapped_column(
        ForeignKey("centers.id", ondelete="CASCADE"),
        nullable=False,
    )

    plan_id: Mapped[int] = mapped_column(
        ForeignKey("ticket_plans.id", ondelete="RESTRICT"),
        nullable=False,
    )

    plan = relationship("TicketPlan")

    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    valid_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    remaining_entries: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,  # NULL = unlimited
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User", back_populates="tickets")
    center = relationship("Center")