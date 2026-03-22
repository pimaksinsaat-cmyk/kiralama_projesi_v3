"""kasa banka sube adi eklendi

Revision ID: e4f9c2a1b7d3
Revises: d3b4c8f1a9e2
Create Date: 2026-03-22 19:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4f9c2a1b7d3'
down_revision = 'd3b4c8f1a9e2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('kasa', schema=None) as batch_op:
        batch_op.add_column(sa.Column('banka_sube_adi', sa.String(length=120), nullable=True))


def downgrade():
    with op.batch_alter_table('kasa', schema=None) as batch_op:
        batch_op.drop_column('banka_sube_adi')
