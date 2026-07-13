"""
Refresh token OPACO: nunca armazenamos o valor bruto, só o hash (SHA-256).

Por que opaco e não JWT:
- JWT de refresh é stateless -> não dá pra revogar antes de expirar
  (logout "de verdade" seria impossível sem uma blocklist).
- Guardando o hash no banco, conseguimos: revogar no logout, rotacionar
  a cada uso (invalida o antigo, emite um novo) e, se quiser evoluir,
  detectar reuso de um token já revogado como sinal de possível roubo.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class RefreshToken(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # SHA-256 do token bruto (64 chars hex). O token bruto só existe na
    # resposta HTTP no momento da emissão — nunca é persistido.
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")  # noqa: F821
