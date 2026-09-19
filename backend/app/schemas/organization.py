from pydantic import BaseModel


class OrganizationCreateRequest(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: int
    name: str
    role: str | None = None

class InviteRequest(BaseModel):
    email: str
    role: str = "member"


class InviteResponse(BaseModel):
    token: str
    organization_id: int
    email: str
    role: str
