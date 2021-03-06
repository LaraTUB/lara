"""Add milestone table

Revision ID: 2cd0988b9a7b
Revises: d5e9375844b9
Create Date: 2018-03-28 03:35:25.555081

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = '2cd0988b9a7b'
down_revision = 'd5e9375844b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    StateTypes = [
        (u'open', u'open'),
        (u'closed', u'closed')
    ]

    op.create_table('milestone',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=1024), nullable=True),
    sa.Column('state', sqlalchemy_utils.types.choice.ChoiceType(StateTypes, impl=sa.String()), nullable=True),
    sa.Column('due_on', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('milestone')
    # ### end Alembic commands ###
