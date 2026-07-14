from __future__ import annotations

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class UsageRecord(TimestampMixin, Base):
    __tablename__ = "usage_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    feature: Mapped[str] = mapped_column(String(50), nullable=False)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # formato "2026-07"
    count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)