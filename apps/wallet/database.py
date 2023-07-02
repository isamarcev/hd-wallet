from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from apps.wallet.models import Wallet, Transaction
from apps.wallet.schemas import CreateWallet, CreateTransactionReceipt
from apps.wallet.models import wallet, transaction

class EthereumDatabase:

    def __init__(self, wallet_model: Type[Wallet],
                 transaction_model: Type[Transaction]):
        self.wallet_model = wallet_model
        self.transaction_model = transaction_model

    async def create_wallet(self, wallet: CreateWallet, db: AsyncSession):
        wallet_instance = self.wallet_model(**wallet.dict())
        db.add(wallet_instance)
        await db.commit()
        print(wallet_instance, "WALLET INSTANCS")
        return wallet_instance

    async def create_transaction(self, transaction: CreateTransactionReceipt, db: AsyncSession):
        transaction_instance = self.transaction_model(**transaction.dict())
        db.add(transaction_instance)
        await db.commit()
        return transaction_instance


    async def get_wallet_by_public_key(self, public_key: str, db: AsyncSession):
        result = await db.execute(
            wallet.select().where(wallet.c.public_key == public_key),
        )
        result_data = result.first()
        return None if not result_data else self.wallet_model(**result_data._asdict())