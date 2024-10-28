import signal
import sys
import traceback
from multiprocessing import Process
import json
from flask import Flask, Response, request
from flask_cors import CORS

from src.config import get_logger
from src.config.errors import AuthError, ECSError
from src.deps_init import (
    credit_limit_svc,
    db_ops,
    emotion_svc,
    env,
    kafka_client,
    thought_svc,
)
from src.models.credit_limit import CreditLimitParams, DeployCreditLimitPayload
from src.models.emotion import KafkaEmotionPayload
from src.models.thought import KafkaThoughtPayload

logger = get_logger(__name__)


def stop_process(process: Process):
    """Stop the Kafka listener process."""
    if process.is_alive():
        process.terminate()  # Send termination signal
        process.join()


def create_app():
    brain_handler_map = {
        "emotion": emotion_svc.handle_kafka_data,
        "thought": thought_svc.handle_kafka_data,
    }
    brain_consumer_proc = Process(
        target=kafka_client.consume,
        args=(env.brain_interface_kafka_topic, brain_handler_map),
    )
    brain_consumer_proc.start()

    def shutdown_handler(signum, frame):
        logger.info("Shutting down...")
        if brain_consumer_proc.is_alive():
            brain_consumer_proc.terminate()  # Send termination signal
            brain_consumer_proc.join()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    new_app = Flask(__name__)
    db_ops.run_migrations()
    return new_app


app = create_app()
CORS(app)


@app.before_request
def check_auth():
    if request.method == "OPTIONS":
        return
    if authorization := request.authorization:
        username, password = authorization.username, authorization.password
        if username != env.auth_username or password != env.auth_password:
            raise AuthError("Invalid credentials")
    else:
        raise AuthError("Invalid credentials")


@app.errorhandler(Exception)
def handle_all_exceptions(e):
    logger.error(e)
    traceback.print_exc()
    return {"error": str(e)}, 500


@app.errorhandler(ECSError)
def handle_ecs_errors(e: ECSError):
    logger.error(e)
    res = Response(
        status=e.code, content_type="application/json"
    )
    res.data = json.dumps({"error": str(e)})
    if e.code == 401:
        res.headers["WWW-Authenticate"] = "Basic"
    return res, e.code


@app.route("/api/credit-limit/calculate", methods=["POST"])
def calculate_credit_limit():
    payload = CreditLimitParams.model_validate(request.get_json())
    credit_limit = credit_limit_svc.calculate_credit_limit(payload)
    return credit_limit.model_dump(mode="json")


@app.route("/api/credit-limit/deploy", methods=["PATCH"])
def deploy_credit_limit():
    payload = DeployCreditLimitPayload.model_validate(request.get_json())
    user = credit_limit_svc.deploy_credit_limit(payload)
    return user.model_dump(mode="json")

def _push_data_to_kafka(payload, data_type):
    kafka_client.publish(env.brain_interface_kafka_topic, payload, key=data_type)


@app.route("/api/brain-data/<data_type>", methods=["POST"])
def insert_brain_data(data_type):
    payload = {**request.get_json(), 'user_id': 'c8a71a0c-812c-4efb-a394-f5f258b4e378'}
    if data_type == "emotion":
        data = KafkaEmotionPayload.model_validate(payload)
    else:
        data = KafkaThoughtPayload.model_validate(payload)
    _push_data_to_kafka(data.model_dump(mode="json"), data_type)
    return 'OK'
