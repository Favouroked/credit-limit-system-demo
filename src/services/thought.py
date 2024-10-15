from typing import List

from src.config import get_logger
from src.db.entities.thought import Thought
from src.db.ops import DBOps
from src.models.thought import KafkaThoughtPayload


class ThoughtService:
    def __init__(self, db_ops: DBOps):
        self._db_ops = db_ops
        self._logger = get_logger(__name__)

    def handle_kafka_data(self, payload: dict):
        data = KafkaThoughtPayload.model_validate(payload)
        new_thought = Thought.model_validate(
            data.model_dump(mode="json")
        )
        self._db_ops.insert_entity(new_thought)

    def retrieve_thought_data(self, payload: dict) -> List[Thought]:
        query = f"""SELECT * FROM {Thought.get_table_name()} 
        WHERE user_id = %(user_id)s AND created_at BETWEEN %(start)s AND %(end)s"""
        result = self._db_ops.run_query(query, payload)
        return [Thought.model_validate(r) for r in result]
