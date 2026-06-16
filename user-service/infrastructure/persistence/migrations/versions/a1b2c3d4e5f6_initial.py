"""initial schema: user_profiles and kyc_inquiries

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-06-16 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.String(36), primary_key=True),
        sa.Column("display_name", sa.String(100), nullable=False, server_default=""),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    kyc_status_enum = sa.Enum(
        "pending", "completed", "failed", "needs_review", "expired",
        name="kyc_status",
    )
    kyc_status_enum.create(op.get_bind())

    op.create_table(
        "kyc_inquiries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("persona_inquiry_id", sa.String(100), nullable=False),
        sa.Column("redirect_url", sa.String(500), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "completed", "failed", "needs_review", "expired",
                name="kyc_status",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_kyc_inquiries_user_id", "kyc_inquiries", ["user_id"])
    op.create_unique_constraint(
        "uq_kyc_inquiries_persona_inquiry_id",
        "kyc_inquiries",
        ["persona_inquiry_id"],
    )
    op.create_index(
        "ix_kyc_inquiries_persona_inquiry_id",
        "kyc_inquiries",
        ["persona_inquiry_id"],
    )


def downgrade() -> None:
    op.drop_table("kyc_inquiries")
    op.drop_table("user_profiles")
    sa.Enum(name="kyc_status").drop(op.get_bind())
