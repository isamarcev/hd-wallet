import json

from eth_account import Account
from fastapi import APIRouter, Depends
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.symbols import ETH
from hdwallet import HDWallet
from hdwallet import BIP44HDWallet
from sqlalchemy.ext.asyncio import AsyncSession

from apps.wallet.dependencies import get_ethereum_manager, get_session
from apps.wallet.manager import EthereumManager

wallet_router = APIRouter()


@wallet_router.post("/create-wallet/")
async def create_wallet(
        manager: EthereumManager = Depends(get_ethereum_manager),
        db_session: AsyncSession = Depends(get_session)
):
    new_wallet = await manager.create_wallet(db_session)
    return new_wallet.dict()


@wallet_router.get("/{wallet}/")
async def create_determinated_wallet(
        wallet: str,
        manager: EthereumManager = Depends(get_ethereum_manager)
):
    print(wallet)

    bip44_hdwallet = BIP44HDWallet(symbol=ETH)
    bip44_hdwallet.from_mnemonic(wallet)

    num_wallets = 5  # Количество дочерних кошельков, которые нужно создать

    child_wallets = []
    for i in range(num_wallets):
        bip44_derivation: BIP44Derivation = BIP44Derivation(
            cryptocurrency=EthereumMainnet, account=0, change=False, address=i
        )
        bip44_hdwallet.from_path(bip44_derivation)
        print(f"({i}) {bip44_hdwallet.path()} {bip44_hdwallet.address()} 0x{bip44_hdwallet.private_key()}")
        child_wallets.append(f"({i}) {bip44_hdwallet.path()} {bip44_hdwallet.address()} 0x{bip44_hdwallet.private_key()} \n")
        bip44_hdwallet.clean_derivation()

    wallets = child_wallets
    print(child_wallets)
    return wallets

