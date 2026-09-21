import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.main import app
from app.models.audit_event import AuditEvent
from app.models.api_key import ApiKey
from app.models.invite import Invite
from app.models.membership import Membership
from app.models.user import User
from app.services.state import reset_store
from app.services.rate_limit import api_key_rate_limiter
from app.core.config import get_settings


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


def test_api_key_full_lifecycle_hides_secret_and_audits_revoke() -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    ).json()["access_token"]
    org_id = client.post(
        "/api/v1/organizations",
        json={"name": "KeysOrg"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]
    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)}

    create_response = client.post("/api/v1/api-keys", json={"name": "CI key"}, headers=headers)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["api_key"].startswith("sk_live_")
    assert created["prefix"] == created["api_key"][:16]

    list_response = client.get("/api/v1/api-keys", headers=headers)
    assert list_response.status_code == 200
    listed = list_response.json()
    assert listed[0]["id"] == created["id"]
    assert "api_key" not in listed[0]
    assert listed[0]["revoked_at"] is None

    async def fetch_key() -> ApiKey | None:
        async with AsyncSessionLocal() as session:
            return await session.get(ApiKey, created["id"])

    persisted_key = asyncio.run(fetch_key())
    assert persisted_key is not None
    assert persisted_key.hashed_key != created["api_key"]

    revoke_response = client.delete(f"/api/v1/api-keys/{created['id']}", headers=headers)
    assert revoke_response.status_code == 204
    assert client.delete(f"/api/v1/api-keys/{created['id']}", headers=headers).status_code == 204

    revoked = client.get("/api/v1/api-keys", headers=headers).json()[0]
    assert revoked["revoked_at"] is not None

    async def fetch_audit_events() -> list[AuditEvent]:
        async with AsyncSessionLocal() as session:
            events = await session.scalars(
                select(AuditEvent).where(
                    AuditEvent.organization_id == org_id,
                    AuditEvent.action == "api_key.revoked",
                )
            )
            return list(events.all())

    assert len(asyncio.run(fetch_audit_events())) == 1


def test_api_key_requires_owner_for_create_and_revoke() -> None:
    for email in ("owner@example.com", "member@example.com"):
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "secret123"},
        )
    owner_token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    ).json()["access_token"]
    member_token = client.post(
        "/api/v1/auth/login",
        json={"email": "member@example.com", "password": "secret123"},
    ).json()["access_token"]
    org_id = client.post(
        "/api/v1/organizations",
        json={"name": "PermissionsOrg"},
        headers={"Authorization": f"Bearer {owner_token}"},
    ).json()["id"]
    owner_headers = {"Authorization": f"Bearer {owner_token}", "X-Organization-Id": str(org_id)}
    member_headers = {"Authorization": f"Bearer {member_token}", "X-Organization-Id": str(org_id)}

    create_response = client.post("/api/v1/api-keys", json={"name": "Owner key"}, headers=owner_headers)
    assert create_response.status_code == 201
    key_id = create_response.json()["id"]

    assert client.post("/api/v1/api-keys", json={"name": "Member key"}, headers=member_headers).status_code == 403
    assert client.delete(f"/api/v1/api-keys/{key_id}", headers=member_headers).status_code == 403


def test_api_key_isolation_blocks_other_organization() -> None:
    for email in ("owner1@example.com", "owner2@example.com"):
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "secret123"},
        )
    token1 = client.post(
        "/api/v1/auth/login",
        json={"email": "owner1@example.com", "password": "secret123"},
    ).json()["access_token"]
    token2 = client.post(
        "/api/v1/auth/login",
        json={"email": "owner2@example.com", "password": "secret123"},
    ).json()["access_token"]
    org1 = client.post(
        "/api/v1/organizations",
        json={"name": "OrgOne"},
        headers={"Authorization": f"Bearer {token1}"},
    ).json()["id"]
    org2 = client.post(
        "/api/v1/organizations",
        json={"name": "OrgTwo"},
        headers={"Authorization": f"Bearer {token2}"},
    ).json()["id"]
    key = client.post(
        "/api/v1/api-keys",
        json={"name": "Private key"},
        headers={"Authorization": f"Bearer {token1}", "X-Organization-Id": str(org1)},
    ).json()
    org2_headers = {"Authorization": f"Bearer {token2}", "X-Organization-Id": str(org2)}

    assert client.delete(f"/api/v1/api-keys/{key['id']}", headers=org2_headers).status_code == 404
    assert client.get("/api/v1/api-keys", headers=org2_headers).json() == []


def test_api_key_rate_limit_rejects_invalid_and_excessive_requests() -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123"},
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "secret123"},
    ).json()["access_token"]
    org_id = client.post(
        "/api/v1/organizations",
        json={"name": "RateLimitOrg"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]
    api_key = client.post(
        "/api/v1/api-keys",
        json={"name": "Rate limit key"},
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": str(org_id)},
    ).json()["api_key"]

    assert client.get("/health", headers={"X-API-Key": "sk_live_invalid"}).status_code == 401

    settings = get_settings()
    original_limit = settings.api_key_rate_limit
    settings.api_key_rate_limit = 1
    api_key_rate_limiter._memory.clear()
    try:
        headers = {"X-API-Key": api_key}
        first = client.get("/health", headers=headers)
        second = client.get("/health", headers=headers)
        assert first.status_code == 200
        assert first.headers["X-RateLimit-Limit"] == "1"
        assert second.status_code == 429
        assert second.headers["Retry-After"]
    finally:
        settings.api_key_rate_limit = original_limit
        api_key_rate_limiter._memory.clear()
