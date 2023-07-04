from sqlalchemy.ext.declarative import declarative_base
import uuid
from sqlalchemy import Column, String, ForeignKey, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import ChoiceType

Base = declarative_base()


class Wallet(Base):
    __tablename__ = "wallet"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String, unique=True)
    public_key = Column(String, unique=True)
    private_key = Column(String, unique=True)
    mnemonic = Column(String)
    parent_wallet = Column(String)


wallet = Wallet.__table__

class Transaction(Base):
    STATUS = [
        ('Success', 'Success'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed')
    ]
    __tablename__ = 'transaction'

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number = Column(String)
    from_address = Column(String)
    to_address = Column(String)
    value = Column(Float)
    date = Column(DateTime(timezone=True), server_default=func.now())
    txn_fee = Column(String)
    status = Column(ChoiceType(STATUS), nullable=False)
    wallet = Column(String)


transaction = Transaction.__table__
