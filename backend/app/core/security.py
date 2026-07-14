from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


# --- Access token (JWT, vida curta) --------------------------------------

def create_access_token(subject: str, *, expires_in_minutes: int | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    ttl = expires_in_minutes or settings.access_token_ttl_minutes

    payload: dict[str, Any] = {
        "sub": subject,
        "token_type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl)).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Retorna None se o token for inválido, expirado, malformado, ou se
    não for do tipo 'access' (ex: alguém tentando usar um refresh token
    direto num endpoint protegido). Nunca deixe JWTError vazar pra camada
    HTTP -- trate aqui e deixe quem chama decidir (normalmente: 401)."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None

    if payload.get("token_type") != "access":
        return None

    return payload


# --- Refresh token (opaco, persistido com hash, revogável) ---------------
# Diferente do access token, NÃO é um JWT: é um valor aleatório de alta
# entropia. Só o hash dele é salvo no banco (tabela refresh_tokens), o que
# permite revogar no logout, rotacionar a cada uso, e -- se quiser evoluir
# depois -- detectar reuso de um token já revogado como sinal de vazamento.

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw_token: str) -> str:
    """SHA-256 (não bcrypt/pbkdf2): o token já nasce aleatório e de alta
    entropia, então não há risco de ataque de dicionário -- não precisamos
    do custo computacional de um KDF de senha, só de um hash rápido e
    determinístico pra permitir lookup no banco."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


def refresh_token_expires_at() -> datetime:
    settings = get_settings()
    return datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_ttl_days)
# --- API Keys (mesmo raciocínio do refresh token: opaca, hash salvo) -----

def generate_api_key() -> str:
    """Gera uma chave no formato sk_live_<random>. O prefixo fixo ajuda a
    identificar o tipo de credencial em logs e em scanners de segredo (o
    GitHub secret scanning, por exemplo, reconhece padrões de prefixo)."""
    return f"sk_live_{secrets.token_urlsafe(32)}"


def hash_api_key(raw_key: str) -> str:
    """Mesma lógica do hash_refresh_token: a chave já nasce aleatória e de
    alta entropia, então SHA-256 simples é suficiente -- não precisamos do
    custo computacional de um KDF de senha aqui."""
    return hashlib.sha256(raw_key.encode()).hexdigest()