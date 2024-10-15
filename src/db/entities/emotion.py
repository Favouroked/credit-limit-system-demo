from typing import List

from src.constants.emotion import EmotionType
from src.db.entities.base import BaseEntity


class Emotion(BaseEntity):
    user_id: str
    emotion_type: EmotionType
    intensity: int

    @classmethod
    def get_table_columns(cls) -> List[str]:
        return [
            "id",
            "user_id",
            "emotion_type",
            "intensity",
            "created_at",
            "updated_at",
        ]

    @classmethod
    def get_table_name(cls) -> str:
        return "emotions"
