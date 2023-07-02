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


class TransactionError(DefaultHTTPException):
    code = "Transaction error"
    type = "Transaction invalid"
    message = "Create transaction error"
    status_code = status.HTTP_400_BAD_REQUEST