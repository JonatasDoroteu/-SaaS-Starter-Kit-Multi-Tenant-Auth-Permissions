from fastapi import APIRouter, HTTPException, status

from app.core.security import create_token, hash_password, verify_password
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.state import store

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> TokenResponse:
    await store.add_user(payload.email, hash_password(payload.password))
    return TokenResponse(
        access_token=create_token(payload.email, token_type="access"),
        refresh_token=create_token(payload.email, token_type="refresh"),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    user = await store.get_user(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(
        access_token=create_token(payload.email, token_type="access"),
        refresh_token=create_token(payload.email, token_type="refresh"),
    )
