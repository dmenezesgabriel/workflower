"""
App logger.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from workflower.config import Config


def set_logger_config(
    name: str,
    log_level: str,
    handlers: list,
) -> logging.Logger:
    """
    Set logger configuration.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    for handler in handlers:
        logger.addHandler(handler)
    return logger


def setup_loggers():
    """
    Configure loggers.
    """

    # Create logging path
    if not os.path.isdir(Config.LOGGING_PATH):
        os.makedirs(Config.LOGGING_PATH)

    log_file_path = os.path.join(Config.LOGGING_PATH, Config.LOGGING_FILE)

    # Set log format
    default_log_format = (
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]"
        " %(message)s"
    )

    #  Set log level
    log_level = getattr(logging, Config.LOG_LEVEL)
    formatter = logging.Formatter(default_log_format)

    # ----------------------------------------------------------------------- #
    # Handlers
    # ----------------------------------------------------------------------- #

    # Console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # File
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=Config.LOGGING_FILE_MAX_BYTES,
        backupCount=Config.LOGGING_FILE_BACKUP_COUNT,
    )
    file_handler.setFormatter(formatter)

    # ----------------------------------------------------------------------- #
    # Loggers
    # ----------------------------------------------------------------------- #

    handlers = [stream_handler, file_handler]
    set_logger_config("workflower", log_level, handlers)
