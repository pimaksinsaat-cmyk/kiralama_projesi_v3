"""kiralama kalemi donus fatura checkbox

Revision ID: c1a4f0b9d3e2
Revises: b7e3c1f4a9d2
Create Date: 2026-03-21 23:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1a4f0b9d3e2'
down_revision = 'b7e3c1f4a9d2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('kiralama_kalemi', schema=None) as batch_op:
        batch_op.add_column(sa.Column('donus_nakliye_fatura_et', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('kiralama_kalemi', schema=None) as batch_op:
        batch_op.drop_column('donus_nakliye_fatura_et')
