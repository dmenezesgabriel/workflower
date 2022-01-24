"""
Alteryx helper module
"""
import logging
import re
from subprocess import PIPE, STDOUT, CalledProcessError, Popen

from workflower.operators.operator import BaseOperator


class AlteryxOperator(BaseOperator):
    @classmethod
    def run_workflow(cls, workflow_file_path: str):
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
                    output["logs"].append(cls.result_parser(decoded_line))
            except CalledProcessError as e:
                logger.error(f"{str(e)}")
        return str(output)

    @classmethod
    def result_parser(cls, output):
        """
        Parse shell execution of Alteryx workflow through
        command line executable AlteryxEngineCmd.exe
        """
        warn = re.compile(r"\d+\swarnings")
        error = re.compile(r"\d+\serrors")
        conversion_err = re.compile(r"\d+\sfield conversion errors")
        # seconds = re.compile(r"\d+\.\d\d\d")

        try:
            warnings = warn.findall(output)[0]
        except Exception:
            warnings = 0
        try:
            errors = error.findall(output)[0]
        except Exception:
            errors = 0
        try:
            conversion = conversion_err.findall(output)[0]
        except Exception:
            conversion = 0

        return {
            "Warnings": warnings,
            "FieldConversionErrors": conversion,
            "Errors": errors,
            "Message": output,
        }
