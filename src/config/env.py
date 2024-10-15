from pydantic import BaseModel


class EnvironmentVariables(BaseModel):
    database_url: str
    kafka_bootstrap_servers: str
    brain_interface_kafka_topic: str
    kafka_consumer_group_id: str
    base_credit_limit: int
    auth_username: str
    auth_password: str
    gcp_credentials: str
    gcp_project_id: str
