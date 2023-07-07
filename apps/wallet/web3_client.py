import logging
from abc import ABC
from decimal import Decimal

from eth_account import Account
from eth_typing import ChecksumAddress, Address
from hdwallet import HDWallet
from hdwallet.symbols import ETH
from hexbytes import HexBytes
from web3 import Web3, eth
from web3.middleware import geth_poa_middleware

from apps.wallet.exeptions import Web3ConnectionError, TransactionError
from config.settings import settings

import mnemonic


class BaseClient(ABC):

    @property
    def provider(self):
        try:
            provider = Web3(Web3.WebsocketProvider(settings.INFURA_API_URL))
            provider.middleware_onion.inject(geth_poa_middleware, layer=0)
            print(f"Is connected: {provider.is_connected()}")
        except Exception:
            raise Web3ConnectionError()
        return provider


class EthereumClient(BaseClient):

    def sync_get_balance(self, address: str):
        checksum_address = Web3.to_checksum_address(address)
        try:
            balance = self.provider.eth.get_balance(checksum_address)
            ether_balance = Web3.from_wei(balance, 'ether')
            return ether_balance
        except Exception as e:
            print(e)
            return



    def sync_send_transaction(self, from_address: str, to_address: str, amount: float, private_key: str):
        try:
            provider = self.provider
            transaction = self.build_txn(provider, from_address, to_address, amount)
            signed_txn = provider.eth.account.sign_transaction(transaction, private_key)
            txn_hash = provider.eth.send_raw_transaction(signed_txn.rawTransaction)
            return txn_hash.hex()
        except Exception as ex:
            raise TransactionError(str(ex))

    def sync_get_balance(self, address: str):
        checksum_address = Web3.to_checksum_address(address)
        try:
            balance = self.provider.eth.get_balance(checksum_address)
        except ValueError:
            print("BEFORE sync GET BALANCE CONNECTION ERROR")
            return self.sync_get_balance(address)
        ether_balance = Web3.from_wei(balance, 'ether')
        return ether_balance

    @staticmethod
    def build_txn(provider: Web3, from_address: str, to_address: str, amount: float):
        gas_price = provider.eth.gas_price
        gas = 21000
        # address = Address(from_address)
        sf = HexBytes(from_address)
        nonce = provider.eth.get_transaction_count(sf, "latest")

        txn = {
            'chainId': provider.eth.chain_id,
            'from': from_address,
            'to': to_address,
            'value': int(Web3.to_wei(amount, 'ether')),
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas,
        }
        return txn

    def sync_get_transaction_receipt(self, txn_hash: str):
        hash_tnx = HexBytes(txn_hash)
        try:
            txn = self.provider.eth.get_transaction_receipt(hash_tnx)
            print(txn, "TXN")
            return txn
        except Exception as e:
            print(e)
            return None

    def get_transaction(self, txn_hash: str):
        hex_hash = HexBytes(txn_hash)
        try:
            txn = self.provider.eth.get_transaction(hex_hash)
            print(txn)
            return txn
        except Exception as E:
            print(E)
            return