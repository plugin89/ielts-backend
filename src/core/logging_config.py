import logging
import sys

def setup_logging():
    # get log level from .env
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    # root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # console output handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))

    # prevent duplicate log
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
