from fastapi import APIRouter, Header, HTTPException

from app.core.security import decode_access_token
from app.services.state import store

router = APIRouter()


@router.get("")
async def get_usage(
    x_organization_id: int | None = Header(default=None, alias="X-Organization-Id"),
    authorization: str | None = Header(default=None, alias="Authorization"),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header is required")
    if x_organization_id is None:
        raise HTTPException(status_code=400, detail="X-Organization-Id header is required")

    owner_email = str(decode_access_token(authorization.split(" ", 1)[1])["sub"])
    membership = await store.get_membership(owner_email, x_organization_id)
    if membership is None:
        raise HTTPException(status_code=403, detail="You are not a member of this organization")

    try:
        return await store.get_usage(x_organization_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Organization not found")