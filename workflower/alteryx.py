"""
Alteryx helper module
"""
from typing import Tuple

import pandas as pd


def run_workflow(path: str) -> pd.DataFrame:
    """
    Run Alteryx workflow through command line executable AlteryxEngineCmd.exe.
    """
    import re
    import sqlite3
    import subprocess
    import time
    from datetime import time as timeobj
    from datetime import timedelta

    import pandas as pd
    from config import Config

    con = sqlite3.connect(Config.WORKFLOWS_EXECUTION_DATABASE_URL)

    def workflow_runner(location: str) -> Tuple:
        """
        Run Alteryx workflow through command line executable
        AlteryxEngineCmd.exe.
        """
        start = time.time()
        try:
            output = subprocess.check_output(
                [
                    r"C:\Program Files\Alteryx\bin\AlteryxEngineCmd.exe",
                    location,
                ],
                timeout=2400,
            )
        except subprocess.CalledProcessError as e:
            output = e.output
        except subprocess.TimeoutExpired:
            output = str(
                "\r\n Timeout Error, workflow finished with 1 errors \r\n"
            ).encode("cp437")
        end = time.time() - start
        return output, end

    def result_parser(output, end) -> pd.DataFrame:
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
                "Module": path.split("\\")[-1][:-5],
                "ModuleFullPath": path,
                "MasterRunTime": current_time,
                "Time": map(lambda x: str(timedelta(seconds=x)), duration),
                "Result": map(
                    lambda x: "Succeded" if (x == 0) else "Failed", errors
                ),
            }
        )
        return workflow

    results, finish = workflow_runner(path)
    _df = result_parser(results, finish)
    _df.to_sql(con=con, name="alteryx_workflows", if_exists="append")

    return _df
