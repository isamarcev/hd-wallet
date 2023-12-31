from sqlalchemy.ext.asyncio import AsyncSession

from apps.wallet.database import EthereumDatabase
from apps.wallet.manager import EthereumManager
from apps.wallet.models import Wallet, Transaction
from apps.wallet.web3_client import EthereumClient
from config.db import async_session


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def get_db():
    return


async def get_client() -> EthereumClient:
    return EthereumClient()


async def get_database() -> EthereumDatabase:
    return EthereumDatabase(Wallet, Transaction)


async def get_ethereum_manager() -> EthereumManager:
    client = await get_client()
    database = await get_database()
    return EthereumManager(client, database)
