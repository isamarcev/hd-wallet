from sqlalchemy.ext.declarative import declarative_base
import uuid
from sqlalchemy import Column, String, ForeignKey, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class Wallet(Base):
    __tablename__ = "wallet"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_key = Column(String, unique=True)
    privet_key = Column(String, unique=True)
    mnemonic = Column(String, unique=True)
    parent_wallet = Column(String)


wallet = Wallet.__table__


