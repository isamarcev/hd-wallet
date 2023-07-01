import logging
from abc import ABC

from eth_account import Account
from hdwallet import HDWallet
from hdwallet.symbols import ETH
from web3 import Web3, eth
from web3.middleware import geth_poa_middleware

from apps.wallet.exeptions import Web3ConnectionError
from config.settings import settings

import mnemonic


class BaseClient(ABC):

    @property
    def provider(self):
        try:
            provider = Web3(Web3.WebsocketProvider(settings.INFURA_API_URL))
            provider.middleware_onion.inject(geth_poa_middleware, layer=0)
            print(f"Is connected: {provider.is_connected()}")
        except:
            print("BEFORE WEB3 CONNECTION ERROR")
            raise Web3ConnectionError()
        return provider


class EthereumClient(BaseClient):

    def sync_get_balance(self, address: str):
        checksum_address = Web3.to_checksum_address(address)
        try:
            balance = self.provider.eth.get_balance(checksum_address)
        except ValueError:
            print("BEFORE sync GET BALANCE CONNECTION ERROR")
            return self.sync_get_balance(address)
        ether_balance = Web3.from_wei(balance, 'ether')
        return ether_balance

