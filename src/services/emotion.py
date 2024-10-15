from typing import List

from src.config import get_logger
from src.db.entities.emotion import Emotion
from src.db.ops import DBOps
from src.models.emotion import KafkaEmotionPayload


class EmotionService:
    def __init__(self, db_ops: DBOps):
        self._db_ops = db_ops
        self._logger = get_logger(__name__)

    def handle_kafka_data(self, payload: dict):
        data = KafkaEmotionPayload.model_validate(payload)
        new_emotion = Emotion.model_validate(data.model_dump())
        self._db_ops.insert_entity(new_emotion)

    def retrieve_emotion_data(self, payload: dict) -> List[Emotion]:
        query = f"""SELECT * FROM {Emotion.get_table_name()} 
        WHERE user_id = %(user_id)s AND created_at BETWEEN %(start)s AND %(end)s"""
        result = self._db_ops.run_query(query, payload)
        return [Emotion.model_validate(r) for r in result]
