from fastapi_helper import DefaultHTTPException
from starlette import status


class Web3ConnectionError(DefaultHTTPException):
    code = "Web3 error"
    type = "Web3 invalid"
    message = "Problem with connection to Web3, please try again later"
    status_code = status.HTTP_400_BAD_REQUEST