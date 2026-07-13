"""
Base declarativa. Todos os models herdam daqui.
Também é o arquivo que o Alembic importa para gerar migrations automaticamente
(por isso importamos todos os models no final).
"""
from datetime import datetime
import uuid

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """Mixin com created_at/updated_at para todos os models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class UUIDMixin:
    """Mixin de PK usando UUID (evita IDs sequenciais previsíveis entre tenants)."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


# Importa os models para que o Alembic "enxergue" as tabelas via Base.metadata.
# Isso é adicionado depois que os models existirem (ver passo 2).
