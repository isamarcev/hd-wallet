from fastapi_helper import DefaultHTTPException
from starlette import status


class Web3ConnectionError(DefaultHTTPException):
    code = "Web3 error"
    type = "Web3 invalid"
    message = "Problem with connection to Web3, please try again later"
    status_code = status.HTTP_400_BAD_REQUEST


class WalletIsNotDefine(DefaultHTTPException):
    code = "Wallet is not defined"
    type = "Wallet invalid"
    message = "This wallet is not defined"
    field = "from_address"
    status_code = status.HTTP_400_BAD_REQUEST


class WalletDoesNotExists(DefaultHTTPException):
    code = "Wallet is not exist"
    type = "Wallet invalid"
    message = "This wallet is not exist"
    field = "from_address"
    status_code = status.HTTP_404_NOT_FOUND


class TransactionError(DefaultHTTPException):
    code = "Transaction error"
    type = "Transaction invalid"
    message = "Create transaction error"
    status_code = status.HTTP_400_BAD_REQUEST


class WalletAddressError(DefaultHTTPException):
    code = "Address error"
    type = "Address invalid"
    message = "Wallet address is invalid"
    status_code = status.HTTP_400_BAD_REQUEST


class MnemonicError(DefaultHTTPException):
    code = "Mnemonic error"
    type = "Mnemonic invalid"
    message = "Mnemonic phrase is invalid"
    status_code = status.HTTP_400_BAD_REQUEST


