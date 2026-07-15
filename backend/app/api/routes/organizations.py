from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_authenticated_email
from app.db import get_db
from app.schemas.organization import InviteRequest, InviteResponse, OrganizationCreateRequest, OrganizationResponse
from app.services.state import store

router = APIRouter()


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    x_organization_id: int | None = Header(default=None, alias="X-Organization-Id"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    session: AsyncSession = Depends(get_db),
) -> list[OrganizationResponse]:
    owner_email = await get_authenticated_email(authorization, session)

    if x_organization_id is None:
        organizations = await store.list_organizations_for_user(owner_email)
        return [OrganizationResponse(id=org["id"], name=org["name"]) for org in organizations]

    membership = await store.get_membership(owner_email, x_organization_id)
    if membership is None:
        raise HTTPException(status_code=403, detail="You are not a member of this organization")

    organization = await store.get_organization(x_organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return [OrganizationResponse(id=organization["id"], name=organization["name"])]


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreateRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
    session: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    owner_email = await get_authenticated_email(authorization, session)
    organization = await store.create_organization(payload.name, owner_email)
    return OrganizationResponse(id=organization["id"], name=organization["name"])


@router.post("/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_invite(
    payload: InviteRequest,
    x_organization_id: int | None = Header(default=None, alias="X-Organization-Id"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    session: AsyncSession = Depends(get_db),
) -> InviteResponse:
    if x_organization_id is None:
        raise HTTPException(status_code=400, detail="X-Organization-Id header is required")

    owner_email = await get_authenticated_email(authorization, session)
    if not await store.can_manage_organization(owner_email, x_organization_id):
        raise HTTPException(status_code=403, detail="Only organization owners can create invites")

    invite = await store.create_invite(organization_id=x_organization_id, email=payload.email, role=payload.role)
    return InviteResponse(
        token=invite["token"],
        organization_id=invite["organization_id"],
        email=invite["email"],
        role=invite["role"],
    )