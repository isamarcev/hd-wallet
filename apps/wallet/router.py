from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.wallet.dependencies import get_ethereum_manager, get_session
from apps.wallet.filters import TransactionFilter
from apps.wallet.manager import EthereumManager
from apps.wallet.schemas import CreateDerivation, SendTransaction, TransactionResult, WalletTransactions, \
    GetMyWallets

ethereum_wallet_router = APIRouter()


@ethereum_wallet_router.get("/create-wallet/")
async def create_wallet(
        manager: EthereumManager = Depends(get_ethereum_manager),
        db_session: AsyncSession = Depends(get_session),
):
    new_wallet = await manager.create_wallet(db_session)
    return new_wallet.dict()


@ethereum_wallet_router.post("/get-my-wallets/")
async def get_wallets(
        request_info: GetMyWallets,
        manager: EthereumManager = Depends(get_ethereum_manager),
        db_session: AsyncSession = Depends(get_session),
):
    wallet_list = await manager.get_user_wallets_by_private_key(request_info, db_session)
    return wallet_list


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
):
    result = await manager.get_transaction_result(tnx_hash)
    return result


@ethereum_wallet_router.get("/get-balance/{address}/")
async def get_balance(
        address: str,
        manager: EthereumManager = Depends(get_ethereum_manager),
):
    result = await manager.get_balance(address)
    return result


@ethereum_wallet_router.get('/get-wallet-transactions/{address}')
async def get_wallet_transaction(
        address: str,
        db: AsyncSession = Depends(get_session),
        manager: EthereumManager = Depends(get_ethereum_manager)
):
    response = await manager.get_wallet_transactions(address, db)
    return response


@ethereum_wallet_router.post('/filter-transactions/')
async def filter_my_transaction(
        transaction_filter: TransactionFilter = FilterDepends(TransactionFilter),
        db: AsyncSession = Depends(get_session),
        manager: EthereumManager = Depends(get_ethereum_manager)
):
    response = await manager.filter_transactions(transaction_filter, db)
    return response

