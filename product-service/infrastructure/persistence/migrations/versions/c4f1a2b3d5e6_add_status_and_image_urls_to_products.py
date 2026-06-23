"""add status and image_urls to products

Revision ID: c4f1a2b3d5e6
Revises: 81ed50ffcb1c
Create Date: 2026-06-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4f1a2b3d5e6"
down_revision: Union[str, None] = "81ed50ffcb1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="processing",
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "image_urls",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
    )


def downgrade() -> None:
    op.drop_column("products", "image_urls")
    op.drop_column("products", "status")
