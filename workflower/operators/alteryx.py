"""
Alteryx helper module
"""
import logging
from subprocess import PIPE, STDOUT, CalledProcessError, Popen

from workflower.config import Config
from workflower.operators.operator import BaseOperator


class AlteryxOperator(BaseOperator):
    @classmethod
    def execute(cls, workflow_file_path: str, *args, **kwargs) -> str:
        """
        Run Alteryx workflow through command line executable
        AlteryxEngineCmd.exe.
        """
        # Logging configuration

        logger = logging.getLogger("workflower.operators.alteryx")
        logger.info(f"Running alteryx workflow: {workflow_file_path}")

        process = Popen(
            [Config.ALTERYX_ENGINE_PATH, workflow_file_path],
            shell=True,
            stdout=PIPE,
            stderr=STDOUT,
        )
        output = {"workflow_path": workflow_file_path, "logs": []}
        with process.stdout:
            try:
                for line in iter(process.stdout.readline, b""):

                    decoded_line = line.decode(
                        "utf-8", errors="ignore"
                    ).rstrip()
                    logger.info(decoded_line)
                    output["logs"].append({"message": decoded_line})
            except CalledProcessError as e:
                logger.error(f"{str(e)}")
        return str(output)
