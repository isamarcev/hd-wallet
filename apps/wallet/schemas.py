import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel


class ConfigBaseModel(BaseModel):
    class Config:
        orm_mode = True


class CreateWallet(ConfigBaseModel):
    parent_wallet: Optional[str]
    public_key: str
    private_key: str
    mnemonic: str


class CreateDerivation(ConfigBaseModel):
    mnemonic: str
    count: int = 1


class SendTransaction(ConfigBaseModel):
    from_address: str
    private_key: str
    to_address: str
    value: float


class StatusEnum(str, Enum):
    success = 'Success'
    pending = 'Pending'
    failed = 'Failed'


class CreateTransactionReceipt(ConfigBaseModel):
    number: str
    from_address: str
    to_address: str
    value: float
    date: datetime.datetime
    txn_fee: Union[None, str]
    status: StatusEnum


class TransactionURL(ConfigBaseModel):
    url: str
    hash: str


class TransactionResult(ConfigBaseModel):
    hash: str


class TransactionInfo(ConfigBaseModel):
    block_number: int
    status: str
    from_address: str
    to_address: str


