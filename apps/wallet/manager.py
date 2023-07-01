from abc import abstractmethod, ABC

import mnemonic
from hdwallet import HDWallet, BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.symbols import ETH
from sqlalchemy.ext.asyncio import AsyncSession

from apps.wallet.database import EthereumDatabase
from apps.wallet.schemas import CreateWallet, CreateDerivation
from apps.wallet.web3_client import EthereumClient


class EthereumManager:

    def __init__(self,
                 client: EthereumClient,
                 database: EthereumDatabase):

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

    async def create_wallet(self, db_session) -> CreateWallet:
        wallet = await self.generate_wallet()
        await self.database.create_wallet(wallet, db_session)
        return wallet


    async def create_derivations(self, request_info: CreateDerivation):
        bip44_hdwallet = BIP44HDWallet(symbol=ETH)
        bip44_hdwallet.from_mnemonic(request_info.mnemonic)

        num_wallets = request_info.count

        child_wallets = []
        for i in range(num_wallets):
            bip44_derivation: BIP44Derivation = BIP44Derivation(
                cryptocurrency=EthereumMainnet, account=0, change=False, address=i
            )
            bip44_hdwallet.from_path(bip44_derivation)
            print(f"({i}) {bip44_hdwallet.path()} {bip44_hdwallet.address()} 0x{bip44_hdwallet.private_key()}")
            child_wallet = CreateWallet(
                public_key=bip44_hdwallet.address(),
                private_key=bip44_hdwallet.private_key(),
                mnemonic=bip44_hdwallet.mnemonic(),

            )
            await self.database.create_wallet(child_wallet, self.db_session)
            child_wallets.append(child_wallet.dict())

            bip44_hdwallet.clean_derivation()

        return child_wallets



