"""add row level security policies

Revision ID: 53862a7c4fbb
Revises: 7a71aa5e193e
Create Date: 2026-09-21 12:39:33.082543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53862a7c4fbb'
down_revision: Union[str, None] = '7a71aa5e193e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TENANT_TABLES = (
    "organizations",
    "memberships",
    "invites",
    "api_keys",
    "audit_events",
    "usage_records",
)


def _policy_expressions(table: str) -> tuple[str, str]:
    tenant_column = "id" if table == "organizations" else "organization_id"
    tenant_context = f"{tenant_column} = current_setting('app.current_org_id', true)::integer"

    if table == "organizations":
        return (
            tenant_context,
            "current_setting('app.allow_org_creation', true) = 'true' OR " + tenant_context,
        )
    if table == "memberships":
        user_context = "user_id = current_setting('app.current_user_id', true)::uuid"
        expression = f"({tenant_context}) OR ({user_context})"
        return expression, expression
    if table == "invites":
        invite_context = "token = current_setting('app.invite_token', true)"
        return f"({tenant_context}) OR ({invite_context})", tenant_context
    return tenant_context, tenant_context


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    for table in TENANT_TABLES:
        using_expression, check_expression = _policy_expressions(table)
        policy_name = f"{table}_tenant_isolation"
        op.execute(sa.text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"DROP POLICY IF EXISTS {policy_name} ON {table}"))
        op.execute(
            sa.text(
                f"CREATE POLICY {policy_name} ON {table} "
                f"USING ({using_expression}) WITH CHECK ({check_expression})"
            )
        )


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    for table in reversed(TENANT_TABLES):
        policy_name = f"{table}_tenant_isolation"
        op.execute(sa.text(f"DROP POLICY IF EXISTS {policy_name} ON {table}"))
        op.execute(sa.text(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY"))