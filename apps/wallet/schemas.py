from typing import Optional

from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    class Config:
        orm_mode = True


class CreateWallet(CustomBaseModel):
    parent_wallet: Optional[str]
    public_key: str
    private_key: str
    mnemonic: str


class CreateDerivation(CustomBaseModel):
    mnemonic: str
    count: int = 1


class GetBalance(CustomBaseModel):
    public_key: str




