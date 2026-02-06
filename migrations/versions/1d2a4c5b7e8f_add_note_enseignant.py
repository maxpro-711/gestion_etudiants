"""add note enseignant

Revision ID: 1d2a4c5b7e8f
Revises: 7f2c3e9a1b04
Create Date: 2026-02-06 12:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1d2a4c5b7e8f"
down_revision = "7f2c3e9a1b04"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("notes") as batch_op:
        batch_op.add_column(sa.Column("enseignant_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_notes_enseignant",
            "users",
            ["enseignant_id"],
            ["id"]
        )


def downgrade():
    with op.batch_alter_table("notes") as batch_op:
        batch_op.drop_constraint("fk_notes_enseignant", type_="foreignkey")
        batch_op.drop_column("enseignant_id")
