from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from apps.wallet.models import Wallet
from apps.wallet.schemas import CreateWallet


class EthereumDatabase:

    def __init__(self, wallet_model: Type[Wallet]):
        self.wallet_model = wallet_model


    async def create_wallet(self, wallet: CreateWallet, db: AsyncSession):
        wallet_instance = self.wallet_model(**wallet.dict())
        db.add(wallet_instance)
        await db.commit()
        return wallet_instance