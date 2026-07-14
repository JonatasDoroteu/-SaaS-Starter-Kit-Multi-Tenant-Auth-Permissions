from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ApiKeyCreateRequest(BaseModel):
    name: str


class ApiKeyCreatedResponse(BaseModel):
    """Retornado só na criação -- é a única vez que a chave completa existe
    em texto puro fora do processo de geração. Depois disso, some pra sempre
    (só o hash fica no banco)."""

    id: int
    name: str
    prefix: str
    api_key: str
    created_at: datetime


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    prefix: str
    created_at: datetime
    last_used_at: datetime | None
    revoked_at: datetime | None