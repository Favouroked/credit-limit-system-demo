from random import randint
from typing import List

from src.config import get_logger
from src.db.entities.emotion import Emotion
from src.db.entities.thought import Thought
from src.db.entities.transaction import Transaction


class MLService:
    def __init__(self):
        self._logger = get_logger(__name__)

    def calculate_risk_score(
        self,
        emotions: List[Emotion],
        thoughts: List[Thought],
        transactions: List[Transaction],
    ):
        fake_base = len(emotions) + len(thoughts) + len(transactions)
        risk_score = randint(fake_base, 850)
        return risk_score
