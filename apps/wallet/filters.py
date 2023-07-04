from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter

from apps.wallet.models import Transaction


class TransactionFilter(Filter):
    from_address: Optional[str]
    wallet: str
    to_address: Optional[str]
    value__lt: Optional[float]
    value__gte: Optional[float]

    class Constants(Filter.Constants):
        model = Transaction
        # ordering_field_name = "date"
        # search_model_fields = ["from_address", "to_address", "value", "wallet"]
