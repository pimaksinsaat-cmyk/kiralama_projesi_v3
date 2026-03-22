"""kiralama kalemi donus nakliye satis alani

Revision ID: b7e3c1f4a9d2
Revises: f2c8b4d9a1e7
Create Date: 2026-03-21 22:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7e3c1f4a9d2'
down_revision = 'f2c8b4d9a1e7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('kiralama_kalemi', schema=None) as batch_op:
        batch_op.add_column(sa.Column('donus_nakliye_satis_fiyat', sa.Numeric(15, 2), nullable=True))


def downgrade():
    with op.batch_alter_table('kiralama_kalemi', schema=None) as batch_op:
        batch_op.drop_column('donus_nakliye_satis_fiyat')
