"""
Alteryx helper module
"""
import logging
import re
import time
from datetime import time as timeobj
from datetime import timedelta
from subprocess import PIPE, STDOUT, CalledProcessError, Popen

import pandas as pd
from workflower.operators.operator import BaseOperator


class AlteryxOperator(BaseOperator):
    @staticmethod
    def run_workflow(workflow_file_path: str):
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
        with process.stdout:
            try:
                for line in iter(process.stdout.readline, b""):
                    decoded_line = line.decode(
                        "utf-8", errors="ignore"
                    ).rstrip()
                    logger.info(decoded_line)

            except CalledProcessError as e:
                logger.error(f"{str(e)}")

    @classmethod
    def result_parser(cls, workflow_file_path, output, end) -> pd.DataFrame:
        """
        Parse shell execution of Alteryx workflow through
        command line executable AlteryxEngineCmd.exe
        """
        warn = re.compile(r"\d+\swarnings")
        error = re.compile(r"\d+\serrors")
        conversion_err = re.compile(r"\d+\sfield conversion errors")
        # seconds = re.compile(r"\d+\.\d\d\d")
        t = time.localtime()
        current_time = time.strftime("%m/%d/%Y %H:%M:%S", t)

        try:
            warnings = [
                int(
                    warn.findall(output.decode("cp437").split("\r\n")[-2])[
                        0
                    ].split(" ")[0]
                )
            ]
        except Exception:
            warnings = [0]

        try:
            errors = [
                int(
                    error.findall(output.decode("cp437").split("\r\n")[-2])[
                        0
                    ].split(" ")[0]
                )
            ]
        except Exception:
            errors = [0]

        try:
            conversion = [
                int(
                    conversion_err.findall(
                        output.decode("cp437").split("\r\n")[-2]
                    )[0].split(" ")[0]
                )
            ]
        except Exception:
            conversion = [0]

        try:
            duration = [end]
        except Exception:
            duration = [timeobj(0, 0, 0)]
        workflow = pd.DataFrame(
            {
                "Output": [output.decode("cp437").split("\r\n")[-2]],
                "Warnings": warnings,
                "FieldConversionErrors": conversion,
                "Errors": errors,
                "Log": [output.decode("cp437")],
                "Module": workflow_file_path.split("\\")[-1][:-5],
                "ModuleFullPath": workflow_file_path,
                "MasterRunTime": current_time,
                "Time": map(lambda x: str(timedelta(seconds=x)), duration),
                "Result": map(
                    lambda x: "Succeded" if (x == 0) else "Failed", errors
                ),
            }
        )
        return workflow
