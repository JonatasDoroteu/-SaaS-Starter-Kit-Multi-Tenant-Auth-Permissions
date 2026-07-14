from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status

from app.api.deps import get_authenticated_email
from app.schemas.api_key import ApiKeyCreatedResponse, ApiKeyCreateRequest, ApiKeyResponse
from app.services.state import store

router = APIRouter()


@router.post("", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreateRequest,
    x_organization_id: int | None = Header(default=None, alias="X-Organization-Id"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> ApiKeyCreatedResponse:
    if x_organization_id is None:
        raise HTTPException(status_code=400, detail="X-Organization-Id header is required")

    owner_email = get_authenticated_email(authorization)
    if not await store.can_manage_organization(owner_email, x_organization_id):
        raise HTTPException(status_code=403, detail="Only organization owners can create API keys")

    result = await store.create_api_key(x_organization_id, payload.name)
    return ApiKeyCreatedResponse(**result)


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(
    x_organization_id: int | None = Header(default=None, alias="X-Organization-Id"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> list[ApiKeyResponse]:
    if x_organization_id is None:
        raise HTTPException(status_code=400, detail="X-Organization-Id header is required")

    owner_email = get_authenticated_email(authorization)
    membership = await store.get_membership(owner_email, x_organization_id)
    if membership is None:
        raise HTTPException(status_code=403, detail="You are not a member of this organization")

    keys = await store.list_api_keys(x_organization_id)
    return [ApiKeyResponse(**k) for k in keys]


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    x_organization_id: int | None = Header(default=None, alias="X-Organization-Id"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> None:
    if x_organization_id is None:
        raise HTTPException(status_code=400, detail="X-Organization-Id header is required")

    owner_email = get_authenticated_email(authorization)
    if not await store.can_manage_organization(owner_email, x_organization_id):
        raise HTTPException(status_code=403, detail="Only organization owners can revoke API keys")

    revoked = await store.revoke_api_key(x_organization_id, key_id)
    if not revoked:
        raise HTTPException(status_code=404, detail="API key not found")