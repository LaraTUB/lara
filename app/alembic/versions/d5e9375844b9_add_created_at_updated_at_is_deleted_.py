"""Add created_at, updated_at, is_deleted colums

Revision ID: d5e9375844b9
Revises: 6f2ffb655543
Create Date: 2018-03-12 20:23:31.494084

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5e9375844b9'
down_revision = '6f2ffb655543'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'is_deleted')
    op.drop_column('user', 'created_at')
    # ### end Alembic commands ###
