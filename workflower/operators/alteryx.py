"""
Alteryx helper module
"""
import logging
from subprocess import PIPE, STDOUT, CalledProcessError, Popen

from workflower.operators.operator import BaseOperator


class AlteryxOperator(BaseOperator):
    @classmethod
    def run_workflow(cls, workflow_file_path: str) -> str:
        """
        Run Alteryx workflow through command line executable
        AlteryxEngineCmd.exe.
        """
        # Logging configuration

        logger = logging.getLogger("alteryx_operator")

        process = Popen(
            [
                r"C:\Program Files\Alteryx\bin\AlteryxEngineCmd.exe",
                workflow_file_path,
            ],
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
