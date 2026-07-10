import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.main import app
from app.models.audit_event import AuditEvent
from app.models.invite import Invite
from app.models.membership import Membership
from app.models.user import User
from app.services.state import reset_store


@pytest.fixture(autouse=True)
def clear_state() -> None:
    reset_store()


client = TestClient(app)


def test_register_and_login_flow() -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    assert response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["access_token"]
    assert payload["refresh_token"]


def test_create_and_list_organization_with_tenant_header() -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    token_response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    token = token_response.json()["access_token"]

    create_response = client.post(
        "/api/v1/organizations",
        json={"name": "Acme"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 201
    org_id = create_response.json()["id"]

    list_response = client.get(
        "/api/v1/organizations",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "Acme"


def test_non_member_cannot_list_organization() -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    client.post(
        "/api/v1/auth/register",
        json={"email": "outsider@example.com", "password": "secret123"},
    )
    owner_token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    ).json()["access_token"]

    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "Gamma"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    org_id = org_response.json()["id"]

    outsider_token = client.post(
        "/api/v1/auth/login",
        json={"email": "outsider@example.com", "password": "secret123"},
    ).json()["access_token"]

    response = client.get(
        "/api/v1/organizations",
        headers={
            "Authorization": f"Bearer {outsider_token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert response.status_code == 403


def test_non_owner_cannot_create_invite() -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    client.post(
        "/api/v1/auth/register",
        json={"email": "member@example.com", "password": "secret123"},
    )
    owner_token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    ).json()["access_token"]
    member_token = client.post(
        "/api/v1/auth/login",
        json={"email": "member@example.com", "password": "secret123"},
    ).json()["access_token"]

    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "Delta"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    org_id = org_response.json()["id"]

    response = client.post(
        "/api/v1/organizations/invites",
        json={"email": "member@example.com", "role": "member"},
        headers={
            "Authorization": f"Bearer {member_token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert response.status_code == 403


def test_admin_can_create_invite() -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    client.post(
        "/api/v1/auth/register",
        json={"email": "admin@example.com", "password": "secret123"},
    )
    owner_token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    ).json()["access_token"]
    admin_token = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "secret123"},
    ).json()["access_token"]

    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "AdminOrg"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    org_id = org_response.json()["id"]

    async def promote_to_admin() -> None:
        async with AsyncSessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == "admin@example.com"))
            membership = await session.scalar(
                select(Membership).where(Membership.user_id == user.id, Membership.organization_id == org_id)
            )
            if membership is None:
                membership = Membership(user_id=user.id, organization_id=org_id, role="admin")
                session.add(membership)
            else:
                membership.role = "admin"
            await session.commit()

    asyncio.run(promote_to_admin())

    response = client.post(
        "/api/v1/organizations/invites",
        json={"email": "member@example.com", "role": "member"},
        headers={
            "Authorization": f"Bearer {admin_token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert response.status_code == 201


def test_create_organization_logs_audit_event() -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    ).json()["access_token"]

    response = client.post(
        "/api/v1/organizations",
        json={"name": "AuditOrg"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201

    async def fetch_events() -> list[AuditEvent]:
        async with AsyncSessionLocal() as session:
            events = await session.scalars(select(AuditEvent).where(AuditEvent.organization_id == response.json()["id"]))
            return list(events.all())

    events = asyncio.run(fetch_events())
    assert len(events) == 1
    assert events[0].action == "organization.created"


def test_cross_tenant_access_is_blocked() -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner1@example.com", "password": "secret123"},
    )
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner2@example.com", "password": "secret123"},
    )
    owner1_token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner1@example.com", "password": "secret123"},
    ).json()["access_token"]

    org_a = client.post(
        "/api/v1/organizations",
        json={"name": "OrgA"},
        headers={"Authorization": f"Bearer {owner1_token}"},
    ).json()

    owner2_token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner2@example.com", "password": "secret123"},
    ).json()["access_token"]
    org_b = client.post(
        "/api/v1/organizations",
        json={"name": "OrgB"},
        headers={"Authorization": f"Bearer {owner2_token}"},
    ).json()

    response = client.get(
        "/api/v1/organizations",
        headers={
            "Authorization": f"Bearer {owner1_token}",
            "X-Organization-Id": str(org_b["id"]),
        },
    )
    assert response.status_code == 403


def test_expired_invite_is_rejected() -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    client.post(
        "/api/v1/auth/register",
        json={"email": "member@example.com", "password": "secret123"},
    )
    owner_token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    ).json()["access_token"]

    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "Epsilon"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    org_id = org_response.json()["id"]

    invite_response = client.post(
        "/api/v1/organizations/invites",
        json={"email": "member@example.com", "role": "member"},
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Organization-Id": str(org_id),
        },
    )
    invite = invite_response.json()

    async def expire_invite() -> None:
        async with AsyncSessionLocal() as session:
            invited = await session.scalar(select(Invite).where(Invite.token == invite["token"]))
            if invited is not None:
                invited.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
                await session.commit()

    asyncio.run(expire_invite())

    response = client.post(
        f"/api/v1/invites/{invite['token']}/accept",
        params={"email": "member@example.com"},
    )
    assert response.status_code == 404


def test_invite_accept_flow() -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    client.post(
        "/api/v1/auth/register",
        json={"email": "member@example.com", "password": "secret123"},
    )
    owner_token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    ).json()["access_token"]

    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "Beta"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    org_id = org_response.json()["id"]

    invite_response = client.post(
        "/api/v1/organizations/invites",
        json={"email": "member@example.com", "role": "member"},
        headers={
            "Authorization": f"Bearer {owner_token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert invite_response.status_code == 201
    invite = invite_response.json()

    accept_response = client.post(
        f"/api/v1/invites/{invite['token']}/accept",
        params={"email": "member@example.com"},
    )
    assert accept_response.status_code == 200
    assert accept_response.json()["status"] == "accepted"
