"""delete index and replace with unique constraints

Revision ID: 7d12ab2ffccb
Revises: 4c374db4615a
Create Date: 2025-09-16 16:28:44.124494

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7d12ab2ffccb"
down_revision = "4c374db4615a"
branch_labels = None
depends_on = None


def upgrade():
    # Supprimer les anciens index partiels
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_index("uq_user_email_active")
        batch_op.drop_index("uq_user_username_active")

        # Créer de vraies contraintes uniques
        batch_op.create_unique_constraint("user_email_key", ["email"])
        batch_op.create_unique_constraint("user_username_key", ["username"])


def downgrade():
    # Supprimer les contraintes uniques
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_constraint("user_email_key", type_="unique")
        batch_op.drop_constraint("user_username_key", type_="unique")

        # Recréer les index partiels
        batch_op.create_index(
            "uq_user_email_active",
            ["email"],
            unique=True,
            postgresql_where=sa.text("deleted_at IS NULL"),
        )
        batch_op.create_index(
            "uq_user_username_active",
            ["username"],
            unique=True,
            postgresql_where=sa.text("deleted_at IS NULL"),
        )
