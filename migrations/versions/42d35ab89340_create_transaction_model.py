"""create transaction model

Revision ID: 42d35ab89340
Revises: d46f71954db0
Create Date: 2023-07-02 13:14:30.506483

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy_utils
# revision identifiers, used by Alembic.
revision = '42d35ab89340'
down_revision = 'd46f71954db0'
branch_labels = None
depends_on = None


STATUS = [
        ('Success', 'Success'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed')
    ]

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('number', sa.String(), nullable=True),
    sa.Column('from_address', sa.String(), nullable=True),
    sa.Column('to_address', sa.String(), nullable=True),
    sa.Column('value', sa.Float(), nullable=True),
    sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('txn_fee', sa.String(), nullable=True),
    sa.Column('status', sqlalchemy_utils.types.choice.ChoiceType(STATUS), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction')
    # ### end Alembic commands ###
