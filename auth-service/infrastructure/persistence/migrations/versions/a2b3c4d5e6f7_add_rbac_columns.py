"""add rbac columns and merchant upgrade requests table

Revision ID: a2b3c4d5e6f7
Revises: 7315473cc688
Create Date: 2026-06-16 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, None] = "7315473cc688"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE user_role AS ENUM ('member', 'merchant', 'operator')")

    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("member", "merchant", "operator", name="user_role"),
            nullable=False,
            server_default="member",
        ),
    )
    op.add_column(
        "users",
        sa.Column("is_merchant_approved", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.create_table(
        "merchant_upgrade_requests",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("reviewer_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_merchant_upgrade_requests_user_id"),
        "merchant_upgrade_requests",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_merchant_upgrade_requests_user_id"),
        table_name="merchant_upgrade_requests",
    )
    op.drop_table("merchant_upgrade_requests")
    op.drop_column("users", "is_merchant_approved")
    op.drop_column("users", "role")
    op.execute("DROP TYPE user_role")
