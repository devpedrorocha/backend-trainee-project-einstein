"""removing subjec_id while it doesn't have subjects

Revision ID: d62ca6f0b03a
Revises: 89a9b9f70484
Create Date: 2024-06-22 09:46:32.692950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd62ca6f0b03a'
down_revision: Union[str, None] = '89a9b9f70484'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('general_questions_ibfk_2', 'general_questions', type_='foreignkey')
    op.drop_column('general_questions', 'subject_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('general_questions', sa.Column('subject_id', mysql.VARCHAR(length=36), nullable=True))
    op.create_foreign_key('general_questions_ibfk_2', 'general_questions', 'subjects', ['subject_id'], ['id'])
    # ### end Alembic commands ###