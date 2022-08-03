"""upgrade piece model 2

Revision ID: 75d1440855cf
Revises: 9f7e6800667a
Create Date: 2022-08-03 18:25:41.706018

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '75d1440855cf'
down_revision = '9f7e6800667a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('piece', sa.Column('tweet_id', sa.Integer(), nullable=False))
    op.drop_column('piece', 'tweet_comments')
    op.drop_column('piece', 'tweet_url')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('piece', sa.Column('tweet_url', mysql.VARCHAR(length=300), nullable=False))
    op.add_column('piece', sa.Column('tweet_comments', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_column('piece', 'tweet_id')
    # ### end Alembic commands ###