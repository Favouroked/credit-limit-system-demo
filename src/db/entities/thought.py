from typing import List

from src.constants.thought import ThoughtSentiment
from src.db.entities.base import BaseEntity


class Thought(BaseEntity):
    user_id: str
    content: str
    sentiment: ThoughtSentiment

    @classmethod
    def get_table_columns(cls) -> List[str]:
        return [
            "id",
            "user_id",
            "content",
            "sentiment",
            "created_at",
            "updated_at",
        ]

    @classmethod
    def get_table_name(cls) -> str:
        return "thoughts"
