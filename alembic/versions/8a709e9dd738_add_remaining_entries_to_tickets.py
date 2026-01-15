"""add remaining_entries to tickets

Revision ID: 8a709e9dd738
Revises: 0b4430cd607e
Create Date: 2026-01-15 16:46:23.090051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a709e9dd738'
down_revision: Union[str, Sequence[str], None] = '0b4430cd607e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'tickets',
        sa.Column('remaining_entries', sa.Integer(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column('tickets', 'remaining_entries')
    # ### end Alembic commands ###
