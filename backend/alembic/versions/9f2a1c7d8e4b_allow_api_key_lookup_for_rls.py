"""allow api key lookup under rls

Revision ID: 9f2a1c7d8e4b
Revises: 53862a7c4fbb
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9f2a1c7d8e4b"
down_revision: Union[str, None] = "53862a7c4fbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_POLICY = "api_keys_tenant_isolation"
_TENANT_EXPRESSION = "organization_id = current_setting('app.current_org_id', true)::integer"
_KEY_EXPRESSION = "hashed_key = current_setting('app.api_key_hash', true)"


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    op.execute(sa.text(f"DROP POLICY IF EXISTS {_POLICY} ON api_keys"))
    op.execute(
        sa.text(
            f"CREATE POLICY {_POLICY} ON api_keys "
            f"USING (({_TENANT_EXPRESSION}) OR ({_KEY_EXPRESSION})) "
            f"WITH CHECK ({_TENANT_EXPRESSION})"
        )
    )


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    op.execute(sa.text(f"DROP POLICY IF EXISTS {_POLICY} ON api_keys"))
    op.execute(
        sa.text(
            f"CREATE POLICY {_POLICY} ON api_keys "
            f"USING ({_TENANT_EXPRESSION}) WITH CHECK ({_TENANT_EXPRESSION})"
        )
    )
