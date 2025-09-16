"""rattrapage user_requests

Revision ID: 175967f134e8
Revises: 738adf70f44a
Create Date: 2025-09-16 22:46:15.865536

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "175967f134e8"
down_revision = "738adf70f44a"
branch_labels = None
depends_on = None


def upgrade():
    # Création de la table user_requests si elle n'existe pas
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'user_requests'
        ) THEN
            CREATE TABLE user_requests (
                id SERIAL PRIMARY KEY,
                username VARCHAR(64) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(84) NOT NULL,
                requested_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        END IF;
    END$$;
    """
    )


def downgrade():
    op.execute(
        """
    DROP TABLE IF EXISTS user_requests CASCADE;
    """
    )
