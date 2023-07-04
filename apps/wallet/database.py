from typing import Type, List, Dict

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from apps.wallet.models import Wallet, Transaction
from apps.wallet.schemas import CreateWallet, CreateTransactionReceipt
from apps.wallet.models import wallet, transaction

class EthereumDatabase:

    def __init__(self, wallet_model: Type[Wallet],
                 transaction_model: Type[Transaction]):
        self.wallet_model = wallet_model
        self.transaction_model = transaction_model

    async def create_wallet(self, wallet: CreateWallet, db: AsyncSession):
        wallet_instance = await db.execute(
            select(self.wallet_model).where(
                self.wallet_model.private_key == wallet.private_key
            )
        )
        existing_wallet = wallet_instance.scalar_one_or_none()

        if existing_wallet:
            return existing_wallet

        wallet_instance = self.wallet_model(**wallet.dict())
        db.add(wallet_instance)
        await db.commit()
        return wallet_instance

    async def create_transaction(self, transaction: CreateTransactionReceipt, db: AsyncSession):
        transaction_instance = self.transaction_model(**transaction.dict())
        db.add(transaction_instance)
        await db.commit()
        return transaction_instance

    async def get_wallet_by_address(self, address: str, db: AsyncSession):
        result = await db.execute(
            wallet.select().where(wallet.c.address == address),
        )
        result_data = result.first()
        return None if not result_data else self.wallet_model(**result_data._asdict())

    async def get_last_transaction(self, wallet: str, db: AsyncSession):
        result = await db.execute(
            select(self.transaction_model).where(
                (((transaction.c.from_address == wallet) | (transaction.c.to_address == wallet)) &
                 (transaction.c.wallet == wallet) & (transaction.c.status != "Pending")
                 )).order_by(transaction.c.date.desc())
        )
        results = result.scalars().first()
        return results

    async def get_wallet_transactions(self, wallet: str, db: AsyncSession):
        result = await db.execute(
            select(self.transaction_model).where(((transaction.c.from_address == wallet) | (transaction.c.to_address == wallet))
                                                 & (transaction.c.wallet == wallet)).order_by(transaction.c.date.desc())
        )

        results = result.scalars().all()
        return results

    async def get_transaction_by_hash(self, hash: str, wallet: str, db: AsyncSession):
        result = await db.execute(
            select(self.transaction_model).where(
                ((transaction.c.number == hash) & (transaction.c.wallet == wallet))
            ))
        results = result.scalars().first()
        return results


    async def update_transaction_by_hash(self, hash: str, wallet: str, data: Dict, db: AsyncSession):
        await db.execute(
            update(self.transaction_model).where(
                ((transaction.c.number == hash) & (transaction.c.wallet == wallet))
            ).values(data))
        await db.commit()


    async def add_transactions(self, transactions: List[CreateTransactionReceipt], db: AsyncSession):
        db.add_all(transactions)
        await db.commit()


    async def get_wallet_by_private_key(self, private_key: str, db: AsyncSession):
        result = await db.execute(
            wallet.select().where(wallet.c.private_key == private_key),
        )
        result_data = result.first()
        return None if not result_data else self.wallet_model(**result_data._asdict())

    async def get_wallets_by_mnemonic(self, mnemonic: str, db: AsyncSession):
        result = await db.execute(
            wallet.select().where(wallet.c.mnemonic == mnemonic),
        )
        return [self.wallet_model(**result_data) for result_data in result.all()]


    async def transaction_filter(self, transaction_filter, db):
        query = select(self.transaction_model)
        query = transaction_filter.filter(query)
        # query = transaction_filter.sort(query)
        print(query, "QUERY")
        result = await db.execute(query)
        print(result)
        return result.scalars().all()