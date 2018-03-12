"""Add user table

Revision ID: 6f2ffb655543
Revises: 
Create Date: 2018-03-12 20:22:04.528540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f2ffb655543'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('github_name', sa.String(length=255), nullable=True),
    sa.Column('github_login', sa.String(length=255), nullable=True),
    sa.Column('github_token', sa.String(length=1024), nullable=True),
    sa.Column('slack_user_id', sa.String(length=255), nullable=True),
    sa.Column('token', sa.String(length=1024), nullable=False),
    sa.Column('state', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
