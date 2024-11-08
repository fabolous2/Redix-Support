"""empty message

Revision ID: e1f3e558682b
Revises: 
Create Date: 2024-06-04 13:09:12.704037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1f3e558682b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('topic_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), server_default='not banned', nullable=False),
    sa.Column('unban_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('info_message', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('topic_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
