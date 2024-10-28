from datetime import datetime
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, model_validator

from src.constants.emotion import EmotionType


class KafkaEmotionPayload(BaseModel):
    id: str
    user_id: str
    emotion_type: EmotionType
    intensity: int
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def populate_default_fields(cls, data: Any) -> Any:
        if "id" not in data:
            data["id"] = str(uuid4())
        if "created_at" not in data:
            data["created_at"] = datetime.utcnow()
        if type(data["created_at"]) in {float, int}:
            created_at = data["created_at"]
            timestamp = (
                created_at if type(created_at) is float else created_at / 1000
            )
            data["created_at"] = datetime.fromtimestamp(timestamp)
        return data

    class Config:
        use_enum_values = True
