"""initial stamp

Revision ID: 504a47d91487
Revises: None
Create Date: 2026-03-11 10:23:14.307795

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "504a47d91487"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
