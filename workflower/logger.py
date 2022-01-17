"""
App logger.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from config import Config


def setup_logger():
    if not os.path.isdir(Config.LOGGING_PATH):
        os.makedirs(Config.LOGGING_PATH)
    log_file_path = os.path.join(Config.LOGGING_PATH, Config.LOGGING_FILE)

    default_log_format = (
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]"
        " %(message)s"
    )
    logger = logging.getLogger()
    formatter = logging.Formatter(default_log_format)
    logger.setLevel(logging.DEBUG)
    # Handlers
    # Console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    # File
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=2000,
        backupCount=10,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
