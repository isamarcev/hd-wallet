"""changed field for publick address

Revision ID: 87d79cc9e70b
Revises: 3eae1e681fcf
Create Date: 2023-07-04 12:37:07.748839

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87d79cc9e70b'
down_revision = '3eae1e681fcf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wallet', sa.Column('address', sa.String(), nullable=True))
    op.drop_constraint('wallet_public_key_key', 'wallet', type_='unique')
    op.create_unique_constraint(None, 'wallet', ['address'])
    op.drop_column('wallet', 'public_key')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wallet', sa.Column('public_key', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'wallet', type_='unique')
    op.create_unique_constraint('wallet_public_key_key', 'wallet', ['public_key'])
    op.drop_column('wallet', 'address')
    # ### end Alembic commands ###
