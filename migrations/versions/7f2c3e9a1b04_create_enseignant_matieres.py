"""create enseignant_matieres

Revision ID: 7f2c3e9a1b04
Revises: 3e4f1c6d2a9f
Create Date: 2026-02-06 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7f2c3e9a1b04"
down_revision = "3e4f1c6d2a9f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "enseignant_matieres",
        sa.Column("enseignant_id", sa.Integer(), nullable=False),
        sa.Column("matiere_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["enseignant_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["matiere_id"], ["matieres.id"]),
        sa.PrimaryKeyConstraint("enseignant_id", "matiere_id"),
    )


def downgrade():
    op.drop_table("enseignant_matieres")
