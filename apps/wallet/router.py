import json
from typing import List

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
from apps.wallet.schemas import CreateDerivation, SendTransaction, TransactionResult, WalletTransactions

ethereum_wallet_router = APIRouter()


@ethereum_wallet_router.get("/create-wallet/")
async def create_wallet(
        manager: EthereumManager = Depends(get_ethereum_manager),
        db_session: AsyncSession = Depends(get_session),
):
    new_wallet = await manager.create_wallet(db_session)
    return new_wallet.dict()


@ethereum_wallet_router.post("/create-derivations/")
async def create_derivations_wallets(
        request_info: CreateDerivation,
        manager: EthereumManager = Depends(get_ethereum_manager),
        db_session: AsyncSession = Depends(get_session),

):
    response = await manager.create_derivations(request_info, db_session)
    return response


@ethereum_wallet_router.post("/send-transaction/")
async def send_transaction(
        transaction_info: SendTransaction,
        manager: EthereumManager = Depends(get_ethereum_manager),
        db_session: AsyncSession = Depends(get_session),
):
    result = await manager.send_transaction(transaction_info, db_session)
    return result


@ethereum_wallet_router.get("/get-transaction-result/{tnx_hash}")
async def get_transaction_result(
        tnx_hash: str,
        manager: EthereumManager = Depends(get_ethereum_manager),
        db_session: AsyncSession = Depends(get_session),
):
    result = await manager.get_transaction_result(tnx_hash, db_session)
    return result


@ethereum_wallet_router.get("/get-balance/{address}/")
async def get_balance(
        address: str,
        manager: EthereumManager = Depends(get_ethereum_manager),
        db_session: AsyncSession = Depends(get_session),
):
    result = await manager.get_balance(address, db_session)
    return result


@ethereum_wallet_router.get("/{wallet}/")
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
        child_wallets.append(
            f"({i}) {bip44_hdwallet.path()} {bip44_hdwallet.address()} 0x{bip44_hdwallet.private_key()} \n")
        bip44_hdwallet.clean_derivation()

    wallets = child_wallets
    print(child_wallets)
    return wallets


@ethereum_wallet_router.get('/get_wallet_transactions/{wallet_id}'
                            # , response_model=List[WalletTransactions]
                            )
async def get_wallet_transaction(
        wallet_id: str,
        db: AsyncSession = Depends(get_session),
        manager: EthereumManager = Depends(get_ethereum_manager)
):
    response = await manager.get_wallet_transactions(wallet_id, db)
    result = [WalletTransactions(number=s.number,
                                 from_address=s.from_address,
                                 to_address=s.to_address,
                                 value=s.value,
                                 txn_fee=float(s.txn_fee),
                                 date=s.date,
                                 status=s.status).dict() for s in response]
    return result
