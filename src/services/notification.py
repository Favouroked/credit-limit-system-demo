import json

from google.oauth2 import service_account
from pyfcm import FCMNotification

from src.db.entities.notification import Notification
from src.db.entities.user import User
from src.db.ops import DBOps
from src.models.notification import NotificationPayload


class NotificationService:
    def __init__(
        self, db_ops: DBOps, gcp_credentials: str, gcp_project_id: str
    ):
        self._db_ops = db_ops

        gcp_json_credentials_dict = json.loads(gcp_credentials)
        credentials = service_account.Credentials.from_service_account_info(
            gcp_json_credentials_dict,
            scopes=["https://www.googleapis.com/auth/firebase.messaging"],
        )
        self._fcm = FCMNotification(
            service_account_file="",
            credentials=credentials,
            project_id=gcp_project_id,
        )

    def create_notification(
        self, user: User, payload: NotificationPayload, cursor=None
    ) -> Notification:
        notification = Notification.model_validate(
            {**payload.model_dump(), "user_id": user.id}
        )
        self._db_ops.insert_entity(notification, cursor=cursor)
        if user.device_token:
            self._fcm.notify(
                fcm_token=user.device_token,
                notification_title=notification.title,
                notification_body=notification.content,
            )
        return notification
