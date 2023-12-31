"""adds user table

Revision ID: 75c65942a949
Revises: f969aba9110a
Create Date: 2023-07-01 21:14:03.868984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75c65942a949'
down_revision = 'f969aba9110a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wallet', sa.Column('private_key', sa.String(), nullable=True))
    op.drop_constraint('wallet_privet_key_key', 'wallet', type_='unique')
    op.create_unique_constraint(None, 'wallet', ['private_key'])
    op.drop_column('wallet', 'privet_key')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wallet', sa.Column('privet_key', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'wallet', type_='unique')
    op.create_unique_constraint('wallet_privet_key_key', 'wallet', ['privet_key'])
    op.drop_column('wallet', 'private_key')
    # ### end Alembic commands ###
