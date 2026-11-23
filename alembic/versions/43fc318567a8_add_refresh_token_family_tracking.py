"""add refresh token family tracking

Revision ID: 43fc318567a8
Revises: fb561b8fa06a
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "43fc318567a8"
down_revision: Union[str, Sequence[str], None] = "fb561b8fa06a"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column(
        "refresh_tokens",
        sa.Column("family_id", sa.Uuid(), nullable=True),
        )


    op.execute(
    "UPDATE refresh_tokens SET family_id = gen_random_uuid() "
    "WHERE family_id IS NULL"
)

    op.alter_column(
    "refresh_tokens",
    "family_id",
    existing_type=sa.Uuid(),
    nullable=False,
)

    op.create_index(
    "ix_refresh_tokens_family_id",
    "refresh_tokens",
    ["family_id"],
    unique=False,
)


def downgrade() -> None:
    op.drop_index(
    "ix_refresh_tokens_family_id",
    table_name="refresh_tokens",
)
    op.drop_column("refresh_tokens", "family_id")
 