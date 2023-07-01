from abc import abstractmethod, ABC

import mnemonic
from hdwallet import HDWallet
from hdwallet.symbols import ETH

from apps.wallet.database import EthereumDatabase
from apps.wallet.schemas import CreateWallet
from apps.wallet.web3_client import EthereumClient


class EthereumManager:

    def __init__(self, client: EthereumClient, database: EthereumDatabase):

        self.client = client
        self.database = database

    async def generate_mnemonic(self):
        mnemo = mnemonic.Mnemonic('english')
        words = mnemo.generate()
        return words

    async def generate_wallet(self) -> CreateWallet:
        mnemo = await self.generate_mnemonic()
        hd_wallet = HDWallet(symbol=ETH, use_default_path=False)
        hd_wallet.from_mnemonic(mnemo)

        new_wallet = CreateWallet(
            public_key=hd_wallet.public_key(),
            private_key=hd_wallet.private_key(),
            mnemonic=hd_wallet.mnemonic()
        )
        return new_wallet

    async def create_wallet(self, db_session):
        wallet = await self.generate_wallet()
        await self.database.create_wallet(wallet, db_session)
        return wallet
