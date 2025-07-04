"""Augmentation chaine de caractere password_hash

Revision ID: 0dba4015ec88
Revises: 74c1ec1c036a
Create Date: 2025-05-09 17:50:50.935565

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0dba4015ec88'
down_revision = '74c1ec1c036a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)

    # ### end Alembic commands ###
