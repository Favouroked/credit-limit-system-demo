from datetime import datetime
from typing import Any

import pytz
from pydantic import BaseModel, model_validator

from src.constants.thought import ThoughtSentiment

timezone = pytz.timezone("UTC")


class KafkaThoughtPayload(BaseModel):
    id: str
    user_id: str
    content: str
    sentiment: ThoughtSentiment
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def populate_default_fields(cls, data: Any) -> Any:
        if type(data["created_at"]) in {float, int}:
            created_at = data["created_at"]
            timestamp = (
                created_at if type(created_at) is float else created_at / 1000
            )
            data["created_at"] = datetime.fromtimestamp(timestamp)
        return data

    class Config:
        use_enum_values = True
