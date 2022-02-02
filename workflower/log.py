"""
App logger.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from workflower.config import Config


def setup_loggers():
    if not os.path.isdir(Config.LOGGING_PATH):
        os.makedirs(Config.LOGGING_PATH)

    log_file_path = os.path.join(Config.LOGGING_PATH, Config.LOGGING_FILE)
    default_log_format = (
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]"
        " %(message)s"
    )
    log_level = getattr(logging, Config.LOG_LEVEL)
    formatter = logging.Formatter(default_log_format)
    # Handlers
    # Console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    # File
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=50000,
        backupCount=3,
    )
    file_handler.setFormatter(formatter)
    # App logger
    app_logger = logging.getLogger("workflower")
    app_logger.setLevel(log_level)
    app_logger.addHandler(stream_handler)
    app_logger.addHandler(file_handler)
    # Scheduler logger
    scheduler_logger = logging.getLogger("apscheduler")
    scheduler_logger.setLevel(log_level)
    scheduler_logger.addHandler(stream_handler)
    scheduler_logger.addHandler(file_handler)
    # Alteryx Operator
    alteryx_logger = logging.getLogger("alteryx_operator")
    alteryx_logger.setLevel(logging.INFO)
    alteryx_logger.addHandler(stream_handler)
    alteryx_logger.addHandler(file_handler)
    # Papermill Operator
    papermill_logger = logging.getLogger("papermill")
    papermill_logger.setLevel(logging.INFO)
    papermill_logger.addHandler(stream_handler)
    papermill_logger.addHandler(file_handler)
