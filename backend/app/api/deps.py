from __future__ import annotations

from fastapi import HTTPException

from app.core.security import decode_access_token


def get_authenticated_email(authorization: str | None) -> str:
    """Valida o header Authorization e retorna o email (sub) do token.
    Lança 401 se o header estiver ausente, malformado, ou o token for
    inválido/expirado."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header is required")

    token_payload = decode_access_token(authorization.split(" ", 1)[1])
    if token_payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return str(token_payload["sub"])