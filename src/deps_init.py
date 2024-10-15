import os

from dotenv import load_dotenv

from src.clients.kafka_client import KafkaClient
from src.config.env import EnvironmentVariables
from src.db.ops import DBOps
from src.services.credit_limit import CreditLimitService
from src.services.emotion import EmotionService
from src.services.ml import MLService
from src.services.notification import NotificationService
from src.services.thought import ThoughtService
from src.services.transaction import TransactionService

load_dotenv()

env = EnvironmentVariables(
    database_url=os.getenv("DATABASE_URL"),
    kafka_bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    brain_interface_kafka_topic=os.getenv("BRAIN_INTERFACE_KAFKA_TOPIC"),
    kafka_consumer_group_id=os.getenv("KAFKA_CONSUMER_GROUP_ID"),
    base_credit_limit=os.getenv("BASE_CREDIT_LIMIT"),
    auth_username=os.getenv("AUTH_USERNAME"),
    auth_password=os.getenv("AUTH_PASSWORD"),
    gcp_credentials=os.getenv("GCP_CREDENTIALS"),
    gcp_project_id=os.getenv("GCP_PROJECT_ID"),
)

# db
db_ops = DBOps(env.database_url)

# clients
kafka_client = KafkaClient(
    env.kafka_bootstrap_servers, env.kafka_consumer_group_id
)

# services
thought_svc = ThoughtService(db_ops)
emotion_svc = EmotionService(db_ops)
ml_svc = MLService()
transaction_svc = TransactionService(db_ops)
notification_svc = NotificationService(
    db_ops, env.gcp_credentials, env.gcp_project_id
)
credit_limit_svc = CreditLimitService(
    env.base_credit_limit,
    db_ops,
    emotion_svc,
    thought_svc,
    transaction_svc,
    ml_svc,
    notification_svc,
)
