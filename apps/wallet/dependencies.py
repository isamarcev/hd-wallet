from sqlalchemy.ext.asyncio import AsyncSession

from apps.wallet.manager import EthereumManager
from apps.wallet.web3_client import EthereumClient
from config.db import async_session


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session



async def get_db():
    return


async def get_client() -> EthereumClient:
    return EthereumClient()


async def get_ethereum_manager() -> EthereumManager:
    client = await get_client()

    return EthereumManager(client)