import asyncio
import datetime
import functools
import json
import logging

import aiohttp
import mnemonic
from eth_keys.datatypes import PrivateKey
from eth_utils import decode_hex
from hdwallet import HDWallet, BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.symbols import ETH
from sqlalchemy.ext.asyncio import AsyncSession
from web3 import Web3

from apps.wallet.database import EthereumDatabase
from apps.wallet.exeptions import WalletIsNotDefine, WalletAddressError, WalletDoesNotExists, MnemonicError, \
    InvalidWalletImport, WalletAlreadyExists
from apps.wallet.models import Transaction
from apps.wallet.schemas import CreateWallet, CreateDerivation, SendTransaction, TransactionURL, \
    CreateTransactionReceipt, WalletTransactions, TransactionInfo, GetMyWallets, MyWallets, WalletImport
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
            address=hd_wallet.p2pkh_address(),
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
        try:
            bip44_hdwallet.from_mnemonic(request_info.mnemonic)
        except ValueError:
            raise MnemonicError()
        parent_address = bip44_hdwallet.address()
        num_wallets = request_info.count

        child_wallets = []
        for i in range(num_wallets):
            bip44_derivation: BIP44Derivation = BIP44Derivation(
                cryptocurrency=EthereumMainnet, account=0, change=False, address=i
            )
            bip44_hdwallet.from_path(bip44_derivation)
            child_wallet = CreateWallet(
                address=bip44_hdwallet.address(),
                private_key=bip44_hdwallet.private_key(),
                mnemonic=bip44_hdwallet.mnemonic(),
                parent_wallet=parent_address

            )
            await self.database.create_wallet(child_wallet, db_session)
            child_wallets.append(child_wallet.dict())

            bip44_hdwallet.clean_derivation()

        return child_wallets

    async def send_transaction(self, transaction_info: SendTransaction, db_session: AsyncSession):
        user_wallet = await self.database.get_wallet_by_address(transaction_info.from_address, db_session)
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

    async def get_transaction_result(self, tnx_data):
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

    async def get_balance(self, address):
        loop = asyncio.get_event_loop()
        current_balance = await loop.run_in_executor(None, functools.partial(self.client.sync_get_balance,
                                                                             address=address,
                                                                             ))
        return current_balance

    async def get_wallet_transactions(self, wallet: str, db: AsyncSession, tnx_filter=None):
        if not Web3.is_address(wallet):
            raise WalletAddressError()
        wallet = wallet.lower()
        transaction = await self.database.get_last_transaction(wallet, db)
        if transaction:
            loop = asyncio.get_running_loop()
            transaction_info = await loop.run_in_executor(None, functools.partial(self.client.sync_get_transaction_receipt,
                                                                                  txn_hash=transaction.number))
            if not transaction_info and not tnx_filter:
                return await self.database.get_wallet_transactions(wallet, db)
            elif not transaction_info and tnx_filter:
                return True
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
                        'txn_fee': '{:.18f}'.format(float(str(Web3.from_wei((int(result['gasPrice']) * int(result['gasUsed'])), 'ether')))),
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
                        txn_fee='{:.18f}'.format(float(str(Web3.from_wei((int(result['gasPrice']) * int(result['gasUsed'])), 'ether')))),
                        status=('Success' if result['txreceipt_status'] == '1' else 'Failed'),
                        wallet=wallet
                    )
                    transactions_list.append(transaction_receipt)
            await self.database.add_transactions(transactions_list, db)
        if tnx_filter:
            return True
        response = await self.database.get_wallet_transactions(wallet, db)
        result = [WalletTransactions(number=s.number,
                                     from_address=s.from_address,
                                     to_address=s.to_address,
                                     value=s.value,
                                     txn_fee=s.txn_fee,
                                     date=s.date,
                                     status=s.status).dict() for s in response]

        return result

    async def get_user_wallets_by_private_key(self, request_info: GetMyWallets, db_session: AsyncSession):
        user_wallet = await self.database.get_wallet_by_private_key(request_info.private_key, db_session)
        if not user_wallet:
            raise WalletDoesNotExists()
        mnemonic = user_wallet.mnemonic
        wallets = await self.database.get_wallets_by_mnemonic(mnemonic, db_session)
        wallet_list = [MyWallets(address=instance.address) for instance in wallets]
        return wallet_list

    async def filter_transactions(self, transaction_filter, db):
        if await self.get_wallet_transactions(transaction_filter.wallet, db, tnx_filter=True) is True:
            result = await self.database.transaction_filter(transaction_filter, db)
            response = [WalletTransactions(number=s.number,
                                     from_address=s.from_address,
                                     to_address=s.to_address,
                                     value=s.value,
                                     txn_fee=f"{float(s.txn_fee):.15f}",
                                     date=s.date,
                                     status=s.status).dict() for s in result]
            return response

    async def import_wallet(self, wallet: WalletImport, db: AsyncSession):
        private_key = wallet.private_key
        try:
            pri_key = decode_hex(private_key)
            pk = PrivateKey(pri_key)
            pub_key = pk.public_key
            public_key = pub_key.to_checksum_address()
        except Exception as e:
            logging.info(f"INVALID {e}")
            raise InvalidWalletImport()
        if await self.database.get_wallet_by_public_key(public_key, db):
            raise WalletAlreadyExists()
        wallet = CreateWallet(private_key=private_key, address=public_key)
        return await self.database.add_wallet(wallet, db)
