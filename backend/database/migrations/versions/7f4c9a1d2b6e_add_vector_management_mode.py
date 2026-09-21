"""add vector infrastructure management mode

Revision ID: 7f4c9a1d2b6e
Revises: 5211725d10a9
Create Date: 2026-08-27 10:20:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f4c9a1d2b6e"
down_revision: str | Sequence[str] | None = "5211725d10a9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


vector_infrastructure_mode = sa.Enum(
    "RAGOPS_MANAGED",
    "CUSTOMER_MANAGED",
    name="vector_infrastructure_mode",
)


def upgrade() -> None:
    """Add vector infrastructure management mode."""
    vector_infrastructure_mode.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.add_column(
        "vector_indexes",
        sa.Column(
            "management_mode",
            vector_infrastructure_mode,
            nullable=False,
            server_default="RAGOPS_MANAGED",
        ),
    )

    op.alter_column(
        "vector_indexes",
        "management_mode",
        server_default=None,
    )


def downgrade() -> None:
    """Remove vector infrastructure management mode."""
    op.drop_column(
        "vector_indexes",
        "management_mode",
    )

    vector_infrastructure_mode.drop(
        op.get_bind(),
        checkfirst=True,
    )