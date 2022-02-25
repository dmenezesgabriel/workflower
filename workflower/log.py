"""
App logger.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from workflower.config import Config


class CsvFormatter(logging.Formatter):
    def format_msg(self, msg):
        """Format the msg to csv string"""
        if isinstance(msg, list):
            msg = ",".join(map(str, msg))
        return msg

    def format(self, record):
        record.msg = self.format_msg(record.msg)
        return logging.Formatter.format(self, record)


class CsvRotatingFileHandler(RotatingFileHandler):
    def __init__(
        self, fmt, datefmt, filename, max_size, max_files, header=None
    ):
        RotatingFileHandler.__init__(
            self, filename, maxBytes=max_size, backupCount=max_files
        )
        self.formatter = CsvFormatter(fmt, datefmt)
        # Format header string if needed
        self._header = header and self.formatter.format_msg(header)

    def rotation_filename(self, default_name):
        """Make log files counter before the .csv extension"""
        s = default_name.rsplit(".", 2)
        return "{}_{:0{}d}.csv".format(
            s[0], int(s[-1]), self.backupCount // 10 + 1
        )

    def doRollover(self):
        """Apped header string to each log file"""
        RotatingFileHandler.doRollover(self)
        if self._header is None:
            return
        f = self.formatter.format
        self.formatter.format = lambda x: x
        self.handle(self._header)
        self.formatter.format = f


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

    # Set log format
    default_log_format = (
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]"
        " %(message)s"
    )
    log_date_format = "%Y-%m-%d %H:%M:%S"

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
    log_file_path = os.path.join(Config.LOGGING_PATH, Config.LOGGING_FILE)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=Config.LOGGING_FILE_MAX_BYTES,
        backupCount=Config.LOGGING_FILE_BACKUP_COUNT,
    )
    file_handler.setFormatter(formatter)

    # CSV
    csv_log_format = (
        "%(asctime)s,%(levelname)s,%(name)s,"
        "%(funcName)s,%(lineno)d,%(message)s"
    )
    csv_log_file_path = os.path.join(Config.CSV_LOGGING_PATH, "log.csv")
    csv_log_header = [
        "asctime",
        "levelname",
        "name",
        "funcName",
        "lineno",
        "message",
    ]
    csv_handler = CsvRotatingFileHandler(
        csv_log_format,
        log_date_format,
        csv_log_file_path,
        Config.LOGGING_FILE_MAX_BYTES,
        Config.LOGGING_FILE_BACKUP_COUNT,
        csv_log_header,
    )
    # ----------------------------------------------------------------------- #
    # Loggers
    # ----------------------------------------------------------------------- #

    handlers = [stream_handler, file_handler, csv_handler]
    set_logger_config("workflower", log_level, handlers)
