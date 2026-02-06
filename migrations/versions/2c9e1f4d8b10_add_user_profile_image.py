"""add user profile image

Revision ID: 2c9e1f4d8b10
Revises: 1d2a4c5b7e8f
Create Date: 2026-02-06 12:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2c9e1f4d8b10"
down_revision = "1d2a4c5b7e8f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("profile_image", sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("profile_image")
