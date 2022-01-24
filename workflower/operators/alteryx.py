"""
Alteryx helper module
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from subprocess import PIPE, STDOUT, CalledProcessError, Popen

from config import Config
from workflower.operators.operator import BaseOperator
from workflower.utils.file import get_file_name


class AlteryxOperator(BaseOperator):
    @staticmethod
    def run_workflow(workflow_file_path: str):
        """
        Run Alteryx workflow through command line executable
        AlteryxEngineCmd.exe.
        """
        # Logging configuration
        default_log_format = (
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]"
            " %(message)s"
        )
        formatter = logging.Formatter(default_log_format)
        # Handlers
        log_file_path = os.path.join(
            Config.LOGGING_PATH, f"{get_file_name(workflow_file_path)}.log"
        )
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=50000,
            backupCount=3,
        )
        file_handler.setFormatter(formatter)
        # File
        alteryx_logger = logging.getLogger("alteryx_operator")
        alteryx_logger.setLevel(logging.INFO)
        alteryx_logger.addHandler(file_handler)

        process = Popen(
            [
                r"C:\Program Files\Alteryx\bin\AlteryxEngineCmd.exe",
                workflow_file_path,
            ],
            shell=True,
            stdout=PIPE,
            stderr=STDOUT,
        )
        with process.stdout:
            try:
                for line in iter(process.stdout.readline, b""):
                    alteryx_logger.info(line)

            except CalledProcessError as e:
                alteryx_logger.error(f"{str(e)}")
