import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.main import app
from app.models.invite import Invite
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
