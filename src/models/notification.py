from pydantic import BaseModel

from src.constants.notification import NotificationType


class NotificationPayload(BaseModel):
    title: str
    content: str
    notification_type: NotificationType
