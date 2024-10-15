import logging
from typing import Optional


def get_logger(
    name: str,
    logging_format: str = "[%(process)d] - %(asctime)s - %(name)s - %(levelname)s - %(message)s",
    file: Optional[str] = None,
) -> logging.Logger:
    logging.basicConfig(format=logging_format)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if file:
        file_handler = logging.FileHandler(file)
        logger.addHandler(file_handler)
    return logger
