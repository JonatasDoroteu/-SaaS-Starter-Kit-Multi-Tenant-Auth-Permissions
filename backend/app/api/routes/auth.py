from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expires_at,
    verify_password,
)
from app.db import get_db
from app.models import RefreshToken, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from sqlalchemy import select

router = APIRouter()


async def _issue_tokens(user: User, session: AsyncSession) -> TokenResponse:
    access_token = create_access_token(subject=str(user.id))

    raw_refresh_token = generate_refresh_token()
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=refresh_token_expires_at(),
    )
    session.add(refresh_token)
    await session.commit()

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh_token)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db)) -> TokenResponse:
    existing = await session.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.email.split("@")[0],
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return await _issue_tokens(user, session)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await session.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return await _issue_tokens(user, session)