from __future__ import annotations

import enum
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.role import Role


class InviteStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    revoked = "revoked"
    expired = "expired"


class Invite(TimestampMixin, Base):
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    invited_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, native_enum=False, length=20), default=Role.member, nullable=False
    )
    status: Mapped[InviteStatus] = mapped_column(
        SAEnum(InviteStatus, native_enum=False, length=20),
        default=InviteStatus.pending,
        nullable=False,
    )
    # BUG CORRIGIDO: era `default=datetime.now(timezone.utc)` (sem lambda),
    # avaliado uma única vez no import -- todo invite tinha o mesmo created_at.
    # O TimestampMixin já resolve isso agora.
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=7),
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship(back_populates="invites")
