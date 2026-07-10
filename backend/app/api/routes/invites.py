from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.state import store

router = APIRouter()


class InviteAcceptResponse(BaseModel):
    status: str
    organization_id: int


@router.post("/{token}/accept", response_model=InviteAcceptResponse)
async def accept_invite(token: str, email: str) -> InviteAcceptResponse:
    result = await store.accept_invite(token, email)
    if result is None:
        raise HTTPException(status_code=404, detail="Invite not found or expired")
    return InviteAcceptResponse(status=result["status"], organization_id=result["organization_id"])
