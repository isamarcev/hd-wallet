from abc import abstractmethod, ABC

from apps.wallet.web3_client import EthereumClient


class EthereumManager:

    def __init__(self, client: EthereumClient):

        self.client = client

    async def create_privet_key(self):
        mnemo = await self.client.generate_mnemonic()
        private_key = await self.client.get_pk_from_mnemonic(mnemo)
        return private_key, mnemo