import json

from eth_account import Account
from fastapi import APIRouter, Depends
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.symbols import ETH
from hdwallet import HDWallet
from hdwallet import BIP44HDWallet

from apps.wallet.dependencies import get_ethereum_manager
from apps.wallet.manager import EthereumManager

wallet_router = APIRouter()

@wallet_router.get("/")
async def create_wallet(
    manager: EthereumManager = Depends(get_ethereum_manager)
):
    # response = await manager.create_new_wallet(user, db)
    private_key, mnemonic = await manager.create_privet_key()

    return {"private_key": private_key, "mnemo": mnemonic}


@wallet_router.get("/{wallet}/")
async def create_determinated_wallet(
        wallet: str,
        manager: EthereumManager = Depends(get_ethereum_manager)
):
    print(wallet)

    bip44_hdwallet = BIP44HDWallet(symbol=ETH)
    bip44_hdwallet.from_mnemonic(wallet)
    # wallet = BIP44HDWallet(symbol=hd_wallet.symbol())

    # base_path = "m/44'/60'/0'/0"  # Базовый путь
    num_wallets = 5  # Количество дочерних кошельков, которые нужно создать
    # hd_wallet.from_path(base_path)
    # Генерация нескольких дочерних кошельков
    child_wallets = []
    for i in range(num_wallets):
        bip44_derivation: BIP44Derivation = BIP44Derivation(
            cryptocurrency=EthereumMainnet, account=0, change=False, address=i
        )
        # path = f"{base_path}/{i}"  # Формирование пути для каждого дочернего кошелька
        bip44_hdwallet.from_path(bip44_derivation)
        print(f"({i}) {bip44_hdwallet.path()} {bip44_hdwallet.address()} 0x{bip44_hdwallet.private_key()}")
        child_wallets.append(f"({i}) {bip44_hdwallet.path()} {bip44_hdwallet.address()} 0x{bip44_hdwallet.private_key()} \n")
        bip44_hdwallet.clean_derivation()

    wallets = child_wallets
    print(child_wallets)
    # Дальнейшая обработка созданных дочерних кошельков
    # for child_wallet in child_wallets:
    #     address = child_wallet.public_key()
    #     private_key = child_wallet.private_key()
    #     wallets.append((address, private_key))
    #


    # num_wallets = 10  # Number of wallets to generate
    # wallets = []
    #
    # hd_wallet = HDWallet(symbol=ETH)
    # hd_wallet.from_mnemonic(wallet)
    # # path = "m/44'/60'/0'/0"
    # # hd_wallet.from_path(path)
    # # print(hd_wallet.private_key(), "PRIVATE KEY WALLET")
    # # test_ew = HDWallet(symbol=ETH)
    # # print(test_ew.from_private_key(hd_wallet.private_key()), "A")
    # # print(json.dumps(hd_wallet.dumps(), indent=4, ensure_ascii=False))
    #
    # # Account.enable_unaudited_hdwallet_features()
    # # master_private_key = Account.from_mnemonic(wallet).key
    # # print(master_private_key)
    # for i in range(num_wallets):
    #     path = f"m/44'/60'/0'/0/{i}"  # Derivation path
    #     child_account = HDWallet(symbol=ETH, use_default_path=False)
    #     child_account.from_path(path)
    #     wallet_address = child_account.public_key()
    #     wallet_private_key = child_account.private_key()
    #     wallets.append((wallet_address, wallet_private_key))

    return wallets

