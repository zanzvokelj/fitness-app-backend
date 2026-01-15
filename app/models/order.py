from datetime import datetime, UTC
from sqlalchemy import ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    ticket_plan_id: Mapped[int] = mapped_column(
        ForeignKey("ticket_plans.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # snapshot price (IMPORTANT!)
    price_cents: Mapped[int] = mapped_column(nullable=False)

    currency: Mapped[str] = mapped_column(
        String(3),
        default="EUR",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )
    # pending | paid | failed | cancelled

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User")
    ticket_plan = relationship("TicketPlan")
    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
    )