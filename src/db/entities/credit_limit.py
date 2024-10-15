from typing import List

from src.db.entities.base import BaseEntity


class CreditLimit(BaseEntity):
    user_id: str
    risk_score: int
    credit_limit: int
    increase: int

    @classmethod
    def get_table_columns(cls) -> List[str]:
        return [
            "id",
            "user_id",
            "risk_score",
            "credit_limit",
            "increase",
            "created_at",
            "updated_at",
        ]

    @classmethod
    def get_table_name(cls) -> str:
        return "credit_limits"
