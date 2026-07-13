from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal, engine
from app.models.audit_event import AuditEvent
from app.models.base import Base
from app.models.invite import Invite
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.core.security import decode_access_token, hash_password


async def initialize_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


class SqlAlchemyStore:
    def __init__(self) -> None:
        self.session_factory = AsyncSessionLocal
        self._initialized = False
        self._init_task: asyncio.Task[None] | None = None
        self._ensure_initialized_sync()

    def _ensure_initialized_sync(self) -> None:
        if self._initialized:
            return
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(initialize_database())
            self._initialized = True
        else:
            self._init_task = asyncio.create_task(initialize_database())

    async def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        if self._init_task is not None:
            await self._init_task
            self._initialized = True
            return
        await initialize_database()
        self._initialized = True

    async def add_user(self, email: str, password_hash: str, full_name: str | None = None) -> dict[str, Any]:
        await self._ensure_initialized()
        async with self.session_factory() as session:
            existing = await session.scalar(select(User).where(User.email == email))
            if existing is not None:
                return {"email": existing.email, "password_hash": existing.hashed_password}
            user = User(
                email=email,
                hashed_password=password_hash,
                full_name=full_name or email.split("@")[0],
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return {"email": user.email, "password_hash": user.hashed_password}

    async def seed_demo_user(self) -> None:
        await self.add_user("demo@example.com", hash_password("secret123"), full_name="Demo User")

    async def get_user(self, email: str) -> dict[str, Any] | None:
        await self._ensure_initialized()
        async with self.session_factory() as session:
            user = await session.scalar(select(User).where(User.email == email))
            if user is None:
                return None
            return {"email": user.email, "password_hash": user.hashed_password}

    async def get_current_user_from_token(self, token: str) -> str | None:
        try:
            payload = decode_access_token(token)
            return str(payload.get("sub")) if payload.get("sub") else None
        except Exception:
            return None

    async def get_organization(self, organization_id: int) -> dict[str, Any] | None:
        await self._ensure_initialized()
        async with self.session_factory() as session:
            organization = await session.get(Organization, organization_id)
            if organization is None:
                return None
            return {"id": organization.id, "name": organization.name}

    async def create_organization(self, name: str, owner_email: str) -> dict[str, Any]:
        await self._ensure_initialized()
        async with self.session_factory() as session:
            user = await session.scalar(select(User).where(User.email == owner_email))
            if user is None:
                user = User(
                    email=owner_email,
                    hashed_password="",
                    full_name=owner_email.split("@")[0],
                )
                session.add(user)
                await session.flush()

            organization = Organization(name=name)
            session.add(organization)
            await session.flush()
            membership = Membership(user_id=user.id, organization_id=organization.id, role="owner")
            session.add(membership)
            audit_event = AuditEvent(
                organization_id=organization.id,
                actor_email=owner_email,
                action="organization.created",
                details=f"Created organization {name}",
            )
            session.add(audit_event)
            await session.commit()
            await session.refresh(organization)
            return {"id": organization.id, "name": organization.name}

    async def list_organizations_for_user(self, email: str) -> list[dict[str, Any]]:
        await self._ensure_initialized()
        async with self.session_factory() as session:
            user = await session.scalar(select(User).where(User.email == email))
            if user is None:
                return []
            memberships = (await session.scalars(select(Membership).where(Membership.user_id == user.id))).all()
            organizations = []
            for membership in memberships:
                organization = await session.get(Organization, membership.organization_id)
                if organization is not None:
                    organizations.append({"id": organization.id, "name": organization.name})
            return organizations

    async def get_membership(self, email: str, organization_id: int) -> dict[str, Any] | None:
        await self._ensure_initialized()
        async with self.session_factory() as session:
            user = await session.scalar(select(User).where(User.email == email))
            if user is None:
                return None
            membership = await session.scalar(
                select(Membership).where(
                    Membership.user_id == user.id,
                    Membership.organization_id == organization_id,
                )
            )
            if membership is None:
                return None
            return {"user_id": user.id, "organization_id": membership.organization_id, "role": membership.role}

    async def can_manage_organization(self, email: str, organization_id: int) -> bool:
        membership = await self.get_membership(email, organization_id)
        return membership is not None and membership["role"] in {"owner", "admin"}

    async def create_invite(self, *, organization_id: int, email: str, role: str) -> dict[str, Any]:
        await self._ensure_initialized()
        async with self.session_factory() as session:
            token = f"inv-{int(datetime.now(timezone.utc).timestamp())}"
            invite = Invite(token=token, organization_id=organization_id, email=email, role=role)
            session.add(invite)
            await session.flush()
            audit_event = AuditEvent(
                organization_id=organization_id,
                actor_email=email,
                action="invite.created",
                details=f"Invited {email} as {role}",
            )
            session.add(audit_event)
            await session.commit()
            await session.refresh(invite)
            return {
                "token": invite.token,
                "organization_id": invite.organization_id,
                "email": invite.email,
                "role": invite.role,
            }

    async def accept_invite(self, token: str, email: str) -> dict[str, Any] | None:
        await self._ensure_initialized()
        async with self.session_factory() as session:
            invite = await session.scalar(select(Invite).where(Invite.token == token))
            if invite is None:
                return None

            expires_at = invite.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < datetime.now(timezone.utc):
                await session.delete(invite)
                await session.commit()
                return None

            user = await session.scalar(select(User).where(User.email == email))
            if user is None:
                return None

            existing_membership = await session.scalar(
                select(Membership).where(
                    Membership.user_id == user.id,
                    Membership.organization_id == invite.organization_id,
                )
            )
            if existing_membership is None:
                membership = Membership(user_id=user.id, organization_id=invite.organization_id, role=invite.role)
                session.add(membership)
            await session.delete(invite)
            audit_event = AuditEvent(
                organization_id=invite.organization_id,
                actor_email=email,
                action="invite.accepted",
                details=f"Accepted invite for organization {invite.organization_id}",
            )
            session.add(audit_event)
            await session.commit()
            return {"status": "accepted", "organization_id": invite.organization_id}


store = SqlAlchemyStore()


async def seed_demo_user() -> None:
    await store.seed_demo_user()


def reset_store() -> None:
    global store
    store = SqlAlchemyStore()