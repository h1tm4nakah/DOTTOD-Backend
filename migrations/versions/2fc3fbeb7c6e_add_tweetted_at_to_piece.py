"""add_tweetted_at_to_piece

Revision ID: 2fc3fbeb7c6e
Revises: 215917110b8c
Create Date: 2022-08-03 22:56:01.249467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fc3fbeb7c6e'
down_revision = '215917110b8c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('piece', sa.Column('tweeted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('piece', 'tweeted_at')
    # ### end Alembic commands ###
