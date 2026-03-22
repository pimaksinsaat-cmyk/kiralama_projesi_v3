"""kasa sube baglanti eklendi

Revision ID: d3b4c8f1a9e2
Revises: 86fa7edfc602
Create Date: 2026-03-22 19:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3b4c8f1a9e2'
down_revision = '86fa7edfc602'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('kasa', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sube_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            batch_op.f('fk_kasa_sube_id_subeler'),
            'subeler',
            ['sube_id'],
            ['id']
        )
        batch_op.create_index(batch_op.f('ix_kasa_sube_id'), ['sube_id'], unique=False)


def downgrade():
    with op.batch_alter_table('kasa', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_kasa_sube_id'))
        batch_op.drop_constraint(batch_op.f('fk_kasa_sube_id_subeler'), type_='foreignkey')
        batch_op.drop_column('sube_id')
