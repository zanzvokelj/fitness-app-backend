from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class TicketPlan(Base):
    __tablename__ = "ticket_plans"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # monthly, yearly, ten-pack, single

    price_cents: Mapped[int] = mapped_column(nullable=False)

    duration_days: Mapped[int | None] = mapped_column(nullable=True)
    # None = (npr. monthly)

    max_entries: Mapped[int | None] = mapped_column(nullable=True)
    # None = unlimited

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)