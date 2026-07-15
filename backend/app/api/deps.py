from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.models.user import User


async def get_authenticated_email(authorization: str | None, session: AsyncSession) -> str:
    """Valida o header Authorization, decodifica o token -- cujo 'sub' é o
    ID do usuário, não o e-mail -- e resolve o e-mail real consultando o
    banco. Lança 401 se o header estiver ausente, malformado, o token for
    inválido/expirado, ou o usuário não existir mais."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header is required")

    token_payload = decode_access_token(authorization.split(" ", 1)[1])
    if token_payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    raw_user_id = token_payload["sub"]
    try:
        user_id = uuid.UUID(raw_user_id)
    except (ValueError, TypeError, AttributeError):
        user_id = raw_user_id

    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user.email