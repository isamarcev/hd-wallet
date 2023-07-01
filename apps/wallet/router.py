from fastapi import APIRouter


wallet_router = APIRouter()

@wallet_router.get("/")
async def create_wallet(
    # manager: EthereumManager = Depends(get_ethereum_manager)
):
    # response = await manager.create_new_wallet(user, db)
    return "Hello"