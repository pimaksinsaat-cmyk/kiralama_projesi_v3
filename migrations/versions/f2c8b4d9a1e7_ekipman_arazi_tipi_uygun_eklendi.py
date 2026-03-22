"""ekipman arazi tipi uygun eklendi

Revision ID: f2c8b4d9a1e7
Revises: 9d4d72a8c6f1
Create Date: 2026-03-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2c8b4d9a1e7'
down_revision = '9d4d72a8c6f1'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ekipman', schema=None) as batch_op:
        batch_op.add_column(sa.Column('arazi_tipi_uygun', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('ekipman', schema=None) as batch_op:
        batch_op.drop_column('arazi_tipi_uygun')
