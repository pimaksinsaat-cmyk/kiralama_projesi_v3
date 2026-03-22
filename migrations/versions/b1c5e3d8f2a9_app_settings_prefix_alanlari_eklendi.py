"""app settings prefix alanları eklendi

Revision ID: b1c5e3d8f2a9
Revises: a91d4c6b8e21
Create Date: 2026-03-23 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c5e3d8f2a9'
down_revision = 'a91d4c6b8e21'
branch_labels = None
depends_on = None


def upgrade():
    # Yeni prefix alanlarını ekle
    with op.batch_alter_table('app_settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('kiralama_form_prefix', sa.String(length=10), nullable=False, server_default='PF')
        )
        batch_op.add_column(
            sa.Column('genel_sozlesme_prefix', sa.String(length=10), nullable=False, server_default='PS')
        )


def downgrade():
    # Alanları kaldır
    with op.batch_alter_table('app_settings', schema=None) as batch_op:
        batch_op.drop_column('genel_sozlesme_prefix')
        batch_op.drop_column('kiralama_form_prefix')
