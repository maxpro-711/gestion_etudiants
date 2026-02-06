"""update users and matiere

Revision ID: 9b8d5c2c4b1a
Revises: 52a79915ea56
Create Date: 2026-02-03 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9b8d5c2c4b1a"
down_revision = "52a79915ea56"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    user_cols = {col["name"] for col in inspector.get_columns("users")}
    with op.batch_alter_table("users") as batch_op:
        if "nom" not in user_cols:
            batch_op.add_column(sa.Column("nom", sa.String(length=100), nullable=True))
        if "prenom" not in user_cols:
            batch_op.add_column(sa.Column("prenom", sa.String(length=100), nullable=True))
        if "matricule" not in user_cols:
            batch_op.add_column(sa.Column("matricule", sa.String(length=50), nullable=True))

    indexes = {idx["name"] for idx in inspector.get_indexes("users")}
    if "ix_users_matricule" not in indexes:
        op.create_index("ix_users_matricule", "users", ["matricule"], unique=True)

    matieres_cols = {col["name"]: col for col in inspector.get_columns("matieres")}
    coefficient_col = matieres_cols.get("coefficient")
    if coefficient_col is not None and isinstance(coefficient_col["type"], sa.Integer):
        with op.batch_alter_table("matieres") as batch_op:
            batch_op.alter_column(
                "coefficient",
                existing_type=sa.Integer(),
                type_=sa.Float(),
                nullable=False
            )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    matieres_cols = {col["name"]: col for col in inspector.get_columns("matieres")}
    coefficient_col = matieres_cols.get("coefficient")
    if coefficient_col is not None and isinstance(coefficient_col["type"], sa.Float):
        with op.batch_alter_table("matieres") as batch_op:
            batch_op.alter_column(
                "coefficient",
                existing_type=sa.Float(),
                type_=sa.Integer(),
                nullable=False
            )

    indexes = {idx["name"] for idx in inspector.get_indexes("users")}
    if "ix_users_matricule" in indexes:
        op.drop_index("ix_users_matricule", table_name="users")

    user_cols = {col["name"] for col in inspector.get_columns("users")}
    with op.batch_alter_table("users") as batch_op:
        if "matricule" in user_cols:
            batch_op.drop_column("matricule")
        if "prenom" in user_cols:
            batch_op.drop_column("prenom")
        if "nom" in user_cols:
            batch_op.drop_column("nom")
