import asyncio
import datetime
import functools
from abc import abstractmethod, ABC

import mnemonic
from hdwallet import HDWallet, BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.symbols import ETH
from sqlalchemy.ext.asyncio import AsyncSession
from web3 import Web3

from apps.wallet.database import EthereumDatabase
from apps.wallet.exeptions import WalletIsNotDefine
from apps.wallet.schemas import CreateWallet, CreateDerivation, SendTransaction, TransactionURL, \
    CreateTransactionReceipt
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


    async def create_derivations(self, request_info: CreateDerivation, db_session):
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
            await self.database.create_wallet(child_wallet, db_session)
            child_wallets.append(child_wallet.dict())

            bip44_hdwallet.clean_derivation()

        return child_wallets


    async def send_transaction(self, transaction_info: SendTransaction, db_session: AsyncSession):
        user_wallet = await self.database.get_wallet_by_public_key(transaction_info.from_address, db_session)
        if not user_wallet:
            raise WalletIsNotDefine()
        if not Web3.is_address(transaction_info.to_address):
            raise WalletIsNotDefine(message='Wallet address is not defined')
        loop = asyncio.get_running_loop()
        txn_hash = await loop.run_in_executor(None, functools.partial(self.client.sync_send_transaction,
                                                                      from_address=transaction_info.from_address,
                                                                      to_address=transaction_info.to_address,
                                                                      amount=transaction_info.value,
                                                                      private_key=transaction_info.private_key))
        transaction_receipt = CreateTransactionReceipt(
            number=txn_hash,
            from_address=transaction_info.from_address.lower(),
            to_address=transaction_info.to_address.lower(),
            value=transaction_info.value,
            date=datetime.datetime.now(),
            txn_fee=None,
            status='Pending',
        )
        await self.database.create_transaction(transaction_receipt, db_session)
        return TransactionURL(url='https://sepolia.etherscan.io/tx/' + txn_hash,
                              hash=txn_hash)



