from typing import List

from src.constants.notification import NotificationType
from src.db.entities.base import BaseEntity


class Notification(BaseEntity):
    title: str
    content: str
    user_id: str
    notification_type: NotificationType

    @classmethod
    def get_table_columns(cls) -> List[str]:
        return [
            "id",
            "title",
            "content",
            "user_id",
            "notification_type",
            "created_at",
            "updated_at",
        ]

    @classmethod
    def get_table_name(cls) -> str:
        return "notifications"
