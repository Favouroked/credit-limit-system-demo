from typing import List

from src.constants.transaction import TransactionType
from src.db.entities.base import BaseEntity


class Transaction(BaseEntity):
    user_id: str
    amount: int
    transaction_type: TransactionType

    @classmethod
    def get_table_columns(cls) -> List[str]:
        return [
            "id",
            "user_id",
            "amount",
            "transaction_type",
            "created_at",
            "updated_at",
        ]

    @classmethod
    def get_table_name(cls) -> str:
        return "transactions"
