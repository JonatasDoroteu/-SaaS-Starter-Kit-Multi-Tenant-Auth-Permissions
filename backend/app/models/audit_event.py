from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AuditEvent(TimestampMixin, Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Trocado de actor_email (str) para actor_id (FK). Guardar só o e-mail
    # "congela" um dado que pode mudar (usuário troca de e-mail) e não
    # sobrevive à exclusão do usuário. Se precisar exibir o e-mail no log,
    # resolve via join com User na hora de listar.
    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    details: Mapped[str | None] = mapped_column(String(500), nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="audit_events")
