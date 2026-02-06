"""create demandes

Revision ID: 3e4f1c6d2a9f
Revises: 9b8d5c2c4b1a
Create Date: 2026-02-03 22:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3e4f1c6d2a9f"
down_revision = "9b8d5c2c4b1a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "demandes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("objet", sa.String(length=120), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("date_ajout", sa.DateTime(), nullable=True),
        sa.Column("etudiant_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["etudiant_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("demandes")
