"""app settings tablosu eklendi

Revision ID: a91d4c6b8e21
Revises: f7a1d2c9e6b4
Create Date: 2026-03-23 12:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a91d4c6b8e21'
down_revision = 'f7a1d2c9e6b4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'app_settings',
        sa.Column('company_name', sa.String(length=150), nullable=False),
        sa.Column('company_short_name', sa.String(length=80), nullable=True),
        sa.Column('logo_path', sa.String(length=255), nullable=False),
        sa.Column('company_address', sa.Text(), nullable=True),
        sa.Column('company_phone', sa.String(length=30), nullable=True),
        sa.Column('company_email', sa.String(length=120), nullable=True),
        sa.Column('company_website', sa.String(length=200), nullable=True),
        sa.Column('invoice_title', sa.String(length=150), nullable=True),
        sa.Column('invoice_address', sa.Text(), nullable=True),
        sa.Column('invoice_tax_office', sa.String(length=100), nullable=True),
        sa.Column('invoice_tax_number', sa.String(length=50), nullable=True),
        sa.Column('invoice_mersis_no', sa.String(length=16), nullable=True),
        sa.Column('invoice_iban', sa.String(length=64), nullable=True),
        sa.Column('invoice_notes', sa.Text(), nullable=True),
        sa.Column('kiralama_form_start_no', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('genel_sozlesme_start_no', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_app_settings')),
    )

    with op.batch_alter_table('app_settings', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_app_settings_is_active'), ['is_active'], unique=False)
        batch_op.create_index(batch_op.f('ix_app_settings_is_deleted'), ['is_deleted'], unique=False)


def downgrade():
    with op.batch_alter_table('app_settings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_app_settings_is_deleted'))
        batch_op.drop_index(batch_op.f('ix_app_settings_is_active'))

    op.drop_table('app_settings')