from datetime import datetime, timedelta
from random import choice, randint, random
from typing import List
from unittest.mock import MagicMock, Mock
from uuid import uuid4

import pytest
from psycopg import Connection

from src.constants.credit_limit import CreditRiskFactor
from src.constants.emotion import EmotionType
from src.constants.thought import ThoughtSentiment
from src.db.entities.credit_limit import CreditLimit
from src.db.entities.emotion import Emotion
from src.db.entities.thought import Thought
from src.db.entities.user import User
from src.db.ops import DBOps
from src.models.credit_limit import CreditLimitParams, DeployCreditLimitPayload
from src.services.credit_limit import CreditLimitService
from src.services.emotion import EmotionService
from src.services.ml import MLService
from src.services.thought import ThoughtService
from src.services.transaction import TransactionService


class TestCreditLimitService:
    def setup_method(self, method):
        self._base_credit_limit = 1000
        self._db_ops = MagicMock(spec=DBOps)
        self._emotion_svc = Mock(spec=EmotionService)
        self._thought_svc = Mock(spec=ThoughtService)
        self._transaction_svc = Mock(spec=TransactionService)
        self._ml_svc = Mock(spec=MLService)
        from src.services.notification import NotificationService

        self._notification_svc = Mock(spec=NotificationService)

        self._emotion_types = list(iter(EmotionType))
        self._db_ops.get_connection.return_value.__enter__.return_value = Mock(
            spec=Connection
        )
        self._test_user = User(
            name="Favour Okedele", email="favouroked@gmail.com"
        )
        self._test_credit_limit = CreditLimit(
            user_id=self._test_user.id,
            risk_score=800,
            credit_limit=2000,
            increase=0,
        )

        self._credit_limit_service = CreditLimitService(
            self._base_credit_limit,
            self._db_ops,
            self._emotion_svc,
            self._thought_svc,
            self._transaction_svc,
            self._ml_svc,
            self._notification_svc,
        )

    def _thoughts_test_data(self) -> List[Thought]:
        positive_thoughts = [
            Thought.model_validate(
                dict(
                    user_id=self._test_user.id,
                    sentiment=ThoughtSentiment.POSITIVE,
                    content="abc, 123",
                )
            )
            for _ in range(7)
        ]
        negative_thoughts = [
            Thought.model_validate(
                dict(
                    user_id=self._test_user.id,
                    sentiment=ThoughtSentiment.NEGATIVE,
                    content="abc, 123",
                )
            )
            for _ in range(4)
        ]
        return [*positive_thoughts, *negative_thoughts]

    def _emotions_test_data(self) -> List[Emotion]:
        return [
            Emotion(
                user_id=self._test_user.id,
                emotion_type=choice(self._emotion_types),
                intensity=i,
            )
            for i in range(10)
        ]

    def test_should_return_correct_risk_factor(self):
        risk_score = 810
        risk_factor = self._credit_limit_service.get_risk_factor(risk_score)
        assert risk_factor == CreditRiskFactor.VERY_LOW_RISK

        risk_score = 600
        risk_factor = self._credit_limit_service.get_risk_factor(risk_score)
        assert risk_factor == CreditRiskFactor.MODERATE_RISK

        risk_score = 450
        risk_factor = self._credit_limit_service.get_risk_factor(risk_score)
        assert risk_factor == CreditRiskFactor.VERY_HIGH_RISK

    def test_should_return_average_emotional_intensity(self):
        emotions = self._emotions_test_data()
        average_intensity = 4.5
        calculated_average_intensity = (
            self._credit_limit_service.get_average_intensity(emotions)
        )
        assert calculated_average_intensity == average_intensity

    def test_should_return_most_frequent_sentiment(self):
        thoughts = self._thoughts_test_data()
        dominant_sentiment = (
            self._credit_limit_service.get_most_frequent_sentiment(thoughts)
        )
        assert dominant_sentiment == ThoughtSentiment.POSITIVE

    def test_should_deploy_credit_limit(self):
        payload = DeployCreditLimitPayload(
            user_id=str(uuid4()), credit_limit_id=str(uuid4())
        )
        self._db_ops.get_entity_by_id.side_effect = [
            self._test_user,
            self._test_credit_limit,
        ]
        updated_user = self._credit_limit_service.deploy_credit_limit(payload)
        self._db_ops.update_entity.assert_called_once()
        assert updated_user.credit_limit_id == self._test_credit_limit.id
        assert (
            updated_user.credit_limit == self._test_credit_limit.credit_limit
        )

    def test_should_adjust_credit_limit_for_positive_sentiments(self):
        test_credit_limit_value = 1000
        thoughts = self._thoughts_test_data()
        emotions = self._emotions_test_data()
        emotions[-1].intensity = 1
        expected_increase = 100
        actual_increase = self._credit_limit_service.adjust_credit_limit(
            test_credit_limit_value, emotions, thoughts
        )
        assert actual_increase == expected_increase

    def test_should_adjust_credit_limit_for_negative_sentiments(self):
        test_credit_limit_value = 1000
        thoughts = [
            Thought.model_validate(
                {**t.model_dump(), "sentiment": ThoughtSentiment.NEGATIVE}
            )
            for t in self._thoughts_test_data()
        ]
        emotions = [
            Emotion.model_validate(
                {**e.model_dump(), "intensity": randint(7, 10)}
            )
            for e in self._emotions_test_data()
        ]
        expected_increase = -150
        actual_increase = self._credit_limit_service.adjust_credit_limit(
            test_credit_limit_value, emotions, thoughts
        )
        assert actual_increase == expected_increase

    def test_should_calculate_credit_limit(self):
        params = CreditLimitParams(
            user_id=self._test_user.id,
            start=datetime.now() - timedelta(days=1),
            end=datetime.now(),
        )
        self._thought_svc.retrieve_thought_data.return_value = (
            self._thoughts_test_data()
        )
        self._emotion_svc.retrieve_emotion_data.return_value = (
            self._emotions_test_data()
        )
        self._transaction_svc.retrieve_transaction_data.return_value = []
        self._ml_svc.calculate_risk_score.return_value = 810

        credit_limit = self._credit_limit_service.calculate_credit_limit(
            params
        )
        expected_credit_limit_value = 2000
        assert credit_limit.credit_limit == expected_credit_limit_value
