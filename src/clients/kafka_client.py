import json
from logging import Logger

from kafka import KafkaConsumer, KafkaProducer

from src.config import get_logger


class KafkaClient:
    def __init__(self, bootstrap_server: str, consumer_group_id: str):
        self._bootstrap_server = bootstrap_server
        self._consumer_group_id = consumer_group_id

    def publish(self, topic: str, data: dict, key: str = None):
        producer = KafkaProducer(
            bootstrap_servers=self._bootstrap_server,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8"),
        )
        producer.send(topic, value=data, key=key)
        producer.flush()

    @staticmethod
    def _call_handler(data: dict, handler_func, logger: Logger):
        try:
            handler_func(data)
        except Exception as e:
            logger.error(f"[Kafka] - Error inserting from kafka: {e}")

    def consume(self, topic: str, handler_map: dict):
        logger = get_logger(__name__)
        logger.info(f"[Kafka] - {topic} consumer started")
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self._bootstrap_server,
            group_id=self._consumer_group_id,
            enable_auto_commit=False,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8"),
        )
        try:
            while True:
                msg = consumer.poll(timeout_ms=1000)
                if not msg:
                    continue
                for value in msg.values():
                    for data in value:
                        logger.info(
                            f"[Kafka Data] - {data.key} - {data.timestamp} - {data.value}"
                        )
                        key = data.key
                        handler = handler_map.get(key, None)
                        if not handler:
                            logger.error(
                                f"[Kafka Data] - {key} handler not found"
                            )
                            continue
                        self._call_handler(data.value, handler, logger)
                consumer.commit()
        except KeyboardInterrupt:
            pass
        finally:
            logger.info(f"[Kafka] -  Closing {topic} consumer")
            consumer.close()
