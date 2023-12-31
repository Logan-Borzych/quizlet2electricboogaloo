"""migration

Revision ID: 7ca5d9aa5045
Revises: 
Create Date: 2023-10-28 15:16:46.379806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ca5d9aa5045'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('term', schema=None) as batch_op:
        batch_op.add_column(sa.Column('definition', sa.String(length=255), nullable=False))
        batch_op.drop_column('definiition')
        batch_op.drop_column('setID')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('term', schema=None) as batch_op:
        batch_op.add_column(sa.Column('setID', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('definiition', sa.VARCHAR(length=255), nullable=False))
        batch_op.drop_column('definition')

    # ### end Alembic commands ###
