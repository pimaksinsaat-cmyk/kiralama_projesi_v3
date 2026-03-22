"""kiralama calisma adresi eklendi

Revision ID: 9d4d72a8c6f1
Revises: 452899df577e
Create Date: 2026-03-21 17:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d4d72a8c6f1'
down_revision = '452899df577e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('kiralama', schema=None) as batch_op:
        batch_op.add_column(sa.Column('makine_calisma_adresi', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('kiralama', schema=None) as batch_op:
        batch_op.drop_column('makine_calisma_adresi')
