from typing import List, Optional

from src.db.entities.base import BaseEntity


class User(BaseEntity):
    name: str
    email: str

    credit_limit: Optional[int] = None
    credit_limit_id: Optional[str] = None

    device_token: Optional[str] = None

    @classmethod
    def get_table_columns(cls) -> List[str]:
        return [
            "id",
            "name",
            "email",
            "credit_limit",
            "credit_limit_id",
            "device_token",
            "created_at",
            "updated_at",
        ]

    @classmethod
    def get_table_name(cls) -> str:
        return "users"
