from datetime import datetime, UTC
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    # stripe

    provider_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    # stripe_session_id

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )
    # pending | succeeded | failed

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    order = relationship("Order", back_populates="payment")