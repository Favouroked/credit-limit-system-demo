from typing import List

from src.config import get_logger
from src.config.errors import InvalidValue
from src.constants.credit_limit import CreditRiskFactor, CreditRiskTier
from src.constants.notification import NotificationType
from src.constants.thought import ThoughtSentiment
from src.db.entities.credit_limit import CreditLimit
from src.db.entities.emotion import Emotion
from src.db.entities.thought import Thought
from src.db.entities.user import User
from src.db.ops import DBOps
from src.models.credit_limit import CreditLimitParams, DeployCreditLimitPayload
from src.models.notification import NotificationPayload
from src.services.emotion import EmotionService
from src.services.ml import MLService
from src.services.notification import NotificationService
from src.services.thought import ThoughtService
from src.services.transaction import TransactionService
from src.utils.circuit_breaker import CircuitBreaker


class CreditLimitService:
    def __init__(
        self,
        base_credit_limit: int,
        db_ops: DBOps,
        emotion_svc: EmotionService,
        thought_svc: ThoughtService,
        transaction_svc: TransactionService,
        ml_svc: MLService,
        notification_svc: NotificationService,
    ):
        self._base_credit_limit = base_credit_limit
        self._db_ops = db_ops
        self._logger = get_logger(__name__)
        self._emotion_svc = emotion_svc
        self._thought_svc = thought_svc
        self._transaction_svc = transaction_svc
        self._ml_svc = ml_svc
        self._notification_svc = notification_svc

        self._credit_limit_adjustment_increase = 0.1
        self._credit_limit_adjustment_decrease = 0.15

        self._cb = CircuitBreaker()

    def calculate_credit_limit(self, params: CreditLimitParams) -> CreditLimit:
        payload = params.model_dump()
        user = self._db_ops.get_entity_by_id(params.user_id, User)
        thoughts = self._thought_svc.retrieve_thought_data(payload)
        self._logger.info(f"[{len(thoughts)}] Thought data retrieved")
        emotions = self._emotion_svc.retrieve_emotion_data(payload)
        self._logger.info(f"[{len(emotions)}] Emotion data retrieved")
        transactions = self._transaction_svc.retrieve_transaction_data(payload)
        self._logger.info(f"[{len(transactions)}] Transaction data retrieved")
        risk_score = self._cb.call(
            self._ml_svc.calculate_risk_score, emotions, thoughts, transactions
        )
        risk_factor = self.get_risk_factor(risk_score)
        credit_limit_value = round(self._base_credit_limit * risk_factor.value)
        credit_limit_increase = self.adjust_credit_limit(
            credit_limit_value, emotions, thoughts
        )
        credit_limit_value += credit_limit_increase
        new_credit_limit = CreditLimit.model_validate(
            {
                "user_id": user.id,
                "risk_score": risk_score,
                "credit_limit": credit_limit_value,
                "increase": credit_limit_increase,
            }
        )
        self._db_ops.insert_entity(new_credit_limit)
        return new_credit_limit

    def adjust_credit_limit(
        self, value: int, emotions: List[Emotion], thoughts: List[Thought]
    ) -> int:
        dominant_sentiment = self.get_most_frequent_sentiment(thoughts)
        average_emotional_intensity = self.get_average_intensity(emotions)
        increase = 0
        if (
            dominant_sentiment == ThoughtSentiment.POSITIVE
            and average_emotional_intensity <= 4
        ):
            increase = self._credit_limit_adjustment_increase * value
        elif (
            dominant_sentiment == ThoughtSentiment.NEGATIVE
            and average_emotional_intensity >= 7
        ):
            decrease = self._credit_limit_adjustment_decrease * value
            increase = -decrease
        return round(increase)

    def deploy_credit_limit(self, payload: DeployCreditLimitPayload) -> User:
        with self._db_ops.get_connection() as db_conn:
            cursor = db_conn.cursor()
            user = self._db_ops.get_entity_by_id(
                payload.user_id, User, cursor=cursor
            )
            credit_limit_obj = self._db_ops.get_entity_by_id(
                payload.credit_limit_id, CreditLimit, cursor=cursor
            )
            user.credit_limit_id = credit_limit_obj.id
            user.credit_limit = credit_limit_obj.credit_limit
            self._db_ops.update_entity(user, cursor=cursor)
            self._notification_svc.create_notification(
                user,
                NotificationPayload(
                    title="Credit Limit Update",
                    content="Your credit limit has been updated",
                    notification_type=NotificationType.CREDIT_LIMIT_UPDATE,
                ),
                cursor=cursor,
            )
            return user

    @staticmethod
    def get_most_frequent_sentiment(
        thoughts: List[Thought],
    ) -> ThoughtSentiment:
        positive_count, negative_count, neutral_count = 0, 0, 0
        for thought in thoughts:
            if thought.sentiment == ThoughtSentiment.POSITIVE.value:
                positive_count += 1
            elif thought.sentiment == ThoughtSentiment.NEGATIVE.value:
                negative_count += 1
            else:
                neutral_count += 1
        count_dict = {
            positive_count: ThoughtSentiment.POSITIVE,
            negative_count: ThoughtSentiment.NEGATIVE,
            neutral_count: ThoughtSentiment.NEUTRAL,
        }
        return count_dict[max(positive_count, negative_count, neutral_count)]

    @staticmethod
    def get_average_intensity(emotions: List[Emotion]) -> float:
        intensity = [e.intensity for e in emotions]
        return sum(intensity) / len(intensity)

    @staticmethod
    def get_risk_factor(risk_score: int) -> CreditRiskFactor:
        for tier in CreditRiskTier:
            tier_range = tier.value
            if tier_range[0] <= risk_score <= tier_range[1]:
                return CreditRiskFactor[tier.name]
        raise InvalidValue("Invalid risk score")
