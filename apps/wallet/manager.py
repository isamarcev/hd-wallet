import asyncio
import datetime
import functools
from abc import abstractmethod, ABC

import aiohttp
import mnemonic
from hdwallet import HDWallet, BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.symbols import ETH
from sqlalchemy.ext.asyncio import AsyncSession
from web3 import Web3

from apps.wallet.database import EthereumDatabase
from apps.wallet.exeptions import WalletIsNotDefine, WalletAddressError
from apps.wallet.models import Transaction
from apps.wallet.schemas import CreateWallet, CreateDerivation, SendTransaction, TransactionURL, \
    CreateTransactionReceipt, TransactionResult, TransactionInfo
from apps.wallet.web3_client import EthereumClient
from config.settings import settings


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

    async def get_transaction_result(self, tnx_data, db_session:AsyncSession ):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, functools.partial(self.client.get_transaction,
                                                                    txn_hash=tnx_data,
                                                                    ))
        if not result:
            return {"status": "PENDING"}
        tnx_response = TransactionInfo(
            status="SUCCESS" if result.get("status") else "FAILED",
            block_number=result.get("blockNumber"),
            from_address=result.get("from"),
            to_address=result.get("to"),
            value=Web3.from_wei(result.get("value"), "ether")
        )
        return tnx_response.dict()

    async def get_balance(self, address, db_session):
        loop = asyncio.get_event_loop()
        current_balance = await loop.run_in_executor(None, functools.partial(self.client.sync_get_balance,
                                                                             address=address,
                                                                             ))
        return current_balance

    async def get_wallet_transactions(self, wallet: str, db: AsyncSession):
        if not Web3.is_address(wallet):
            raise WalletAddressError()
        wallet = wallet.lower()
        transaction = await self.database.get_last_transaction(wallet, db)
        if transaction:
            loop = asyncio.get_running_loop()
            transaction_info = await loop.run_in_executor(None, functools.partial(self.client.sync_get_transaction_receipt,
                                                                                  txn_hash=transaction.number))
            if not transaction_info:
                return await self.database.get_wallet_transactions(wallet, db)
            block_number = transaction_info.blockNumber
        else:
            block_number = '0'
        params = {'module': 'account', 'action': 'txlist', 'address': wallet,
                  'startblock': block_number, 'endblock': '99999999',
                  'sort': 'asc', 'apikey': settings.ETHERSCAN_KEY}
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=settings.ETHERSCAN_ENDPOINT, params=params)
            transactions = await response.json()
        if response.status == 200:
            results = transactions['result']
            transactions_list = list()
            for result in results:
                if await self.database.get_transaction_by_hash(result['hash'], wallet, db):
                    data = {
                        'date': datetime.datetime.fromtimestamp(int(result['timeStamp'])),
                        'txn_fee': str(Web3.from_wei((int(result['gasPrice']) * int(result['gasUsed'])), 'ether')),
                        'status': ('Success' if result['txreceipt_status'] == '1' else 'Failed')
                    }
                    await self.database.update_transaction_by_hash(result['hash'], wallet, data, db)
                else:
                    transaction_receipt = Transaction(
                        number=result['hash'],
                        from_address=result['from'],
                        to_address=result['to'],
                        value=float(Web3.from_wei(int(result['value']), 'ether')),
                        date=datetime.datetime.fromtimestamp(int(result['timeStamp'])),
                        txn_fee=str(Web3.from_wei((int(result['gasPrice']) * int(result['gasUsed'])), 'ether')),
                        status=('Success' if result['txreceipt_status'] == '1' else 'Failed'),
                        wallet=wallet
                    )
                    transactions_list.append(transaction_receipt)
            await self.database.add_transactions(transactions_list, db)
        else:
            return await self.database.get_wallet_transactions(wallet, db)
        x = await self.database.get_wallet_transactions(wallet, db)
        print(x, "X")
        return x