"""add column number_question to GeneralQuestion

Revision ID: 89a9b9f70484
Revises: 
Create Date: 2024-06-22 09:30:19.738971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89a9b9f70484'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('general_questions', sa.Column('number_question', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('general_questions', 'number_question')
    # ### end Alembic commands ###