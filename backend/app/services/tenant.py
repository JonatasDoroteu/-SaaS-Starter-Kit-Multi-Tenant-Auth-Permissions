from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request, status

from app.services.state import store


async def require_tenant_access(request: Request) -> dict[str, Any]:
    authorization = request.headers.get("authorization")
    organization_id = request.headers.get("x-organization-id")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is required")

    if not organization_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Organization-Id header is required")

    token = authorization.split(" ", 1)[1]
    owner_email = str((await store.get_current_user_from_token(token)) or "")
    if not owner_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    membership = await store.get_membership(owner_email, int(organization_id))
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this organization")

    return {"email": owner_email, "organization_id": int(organization_id), "role": membership["role"]}
