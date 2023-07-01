from fastapi import APIRouter

from apps.wallet.router import wallet_router

# from base_api.apps.chat.views import chat_router
# from base_api.apps.ethereum.views import ethereum_router
# from base_api.apps.ibay.views import ibay_router
# from base_api.apps.users.views import user_router

router = APIRouter(
    prefix="/api",
)

router.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])