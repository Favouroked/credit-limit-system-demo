from datetime import datetime
from random import choice, randint
from uuid import uuid4

import pytz
from faker import Faker

from src.config import get_logger
from src.constants.emotion import EmotionType
from src.constants.thought import ThoughtSentiment
from src.constants.transaction import TransactionType
from src.db.entities.transaction import Transaction
from src.db.entities.user import User
from src.deps_init import db_ops, env, kafka_client
from src.models.emotion import KafkaEmotionPayload
from src.models.thought import KafkaThoughtPayload

logger = get_logger(__name__)
fake = Faker()
timezone = pytz.timezone("UTC")


def create_user():
    try:
        new_user = User(name="Favour Okedele", email="favouroked@gmail.com")
        db_ops.insert_entity(new_user)
        return new_user
    except Exception as e:
        logger.error(e)


def create_transactions(user: User):
    transaction_types = list(iter(TransactionType))
    with db_ops.get_connection() as conn:
        cursor = conn.cursor()
        for _ in range(100):
            db_ops.insert_entity(
                Transaction(
                    user_id=user.id,
                    amount=randint(100, 10000),
                    transaction_type=choice(transaction_types),
                ),
                cursor=cursor,
            )


def push_emotions(user: User):
    emotion_types = list(iter(EmotionType))
    for _ in range(100):
        payload = dict(
            id=str(uuid4()),
            user_id=user.id,
            emotion_type=choice(emotion_types).value,
            intensity=randint(1, 10),
            created_at=datetime.utcnow().timestamp(),
        )
        kafka_client.publish(
            env.brain_interface_kafka_topic,
            payload,
            key="emotion",
        )


def push_thoughts(user: User):
    sentiment_type = list(iter(ThoughtSentiment))
    for _ in range(100):
        payload = dict(
            id=str(uuid4()),
            user_id=user.id,
            sentiment=choice(sentiment_type).value,
            content=f"{fake.name()} {fake.catch_phrase()}",
            created_at=datetime.utcnow().timestamp(),
        )
        kafka_client.publish(
            env.brain_interface_kafka_topic,
            payload,
            key="thought",
        )


def main():
    logger.info("Running migrations")
    db_ops.run_migrations()
    logger.info("Creating User")
    # user = create_user()
    user = User.model_validate(
        {'id': 'c8a71a0c-812c-4efb-a394-f5f258b4e378', 'created_at': '2024-10-15T16:27:03.098749Z', 'updated_at': '2024-10-15T16:27:03.098753Z', 'name': 'Favour Okedele', 'email': 'favouroked@gmail.com', 'credit_limit': None, 'credit_limit_id': None, 'device_token': None}
    )
    logger.info(f"User: {user.model_dump(mode='json')}")
    # logger.info("Creating Transactions")
    # create_transactions(user)
    # logger.info("Pushing Emotions")
    # push_emotions(user)
    logger.info("Pushing Thoughts")
    push_thoughts(user)


if __name__ == "__main__":
    main()
