from abc import ABC

from web3 import Web3
from web3.middleware import geth_poa_middleware

from config.settings import settings


class BaseClient(ABC):

    @property
    def provider(self):
        try:
            provider = Web3(Web3.WebsocketProvider(settings.infura_api_url))
            provider.middleware_onion.inject(geth_poa_middleware, layer=0)
            print(f"Is connected: {provider.isConnected()}")
        except:
            print("BEFORE WEB3 CONNECTION ERROR")
            raise Web3ConnectionError()
        return provider


class EthereumClient(BaseClient):

    def sync_get_balance(self, address: str) -> str:
        checksum_address = Web3.toChecksumAddress(address)
        try:
            balance = self.provider.eth.get_balance(checksum_address)
        except ValueError:
            print("BEFORE sync GET BALANCE CONNECTION ERROR")
            return self.sync_get_balance(address)
        ether_balance = Web3.fromWei(balance, 'ether')
        return ether_balance