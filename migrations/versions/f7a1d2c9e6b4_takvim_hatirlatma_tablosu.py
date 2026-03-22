"""takvim hatirlatma tablosu

Revision ID: f7a1d2c9e6b4
Revises: e4f9c2a1b7d3
Create Date: 2026-03-22 20:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7a1d2c9e6b4'
down_revision = 'e4f9c2a1b7d3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'takvim_hatirlatma',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tarih', sa.Date(), nullable=False),
        sa.Column('baslik', sa.String(length=150), nullable=False),
        sa.Column('aciklama', sa.Text(), nullable=True),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_takvim_hatirlatma_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_takvim_hatirlatma')),
    )
    with op.batch_alter_table('takvim_hatirlatma', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_takvim_hatirlatma_user_id'), ['user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_takvim_hatirlatma_tarih'), ['tarih'], unique=False)
        batch_op.create_index(batch_op.f('ix_takvim_hatirlatma_is_active'), ['is_active'], unique=False)
        batch_op.create_index(batch_op.f('ix_takvim_hatirlatma_is_deleted'), ['is_deleted'], unique=False)


def downgrade():
    with op.batch_alter_table('takvim_hatirlatma', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_takvim_hatirlatma_is_deleted'))
        batch_op.drop_index(batch_op.f('ix_takvim_hatirlatma_is_active'))
        batch_op.drop_index(batch_op.f('ix_takvim_hatirlatma_tarih'))
        batch_op.drop_index(batch_op.f('ix_takvim_hatirlatma_user_id'))

    op.drop_table('takvim_hatirlatma')
