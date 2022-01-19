from io import StringIO as StringBuffer

import pandas as pd


def run_notebook(input_path, output_path) -> pd.DataFrame:
    import json
    import logging
    import os
    import re

    import pandas as pd

    # TODO
    # Change logger to CSV formatter
    # limit workbook output log with custom filter
    from pythonjsonlogger import jsonlogger

    import papermill as pm

    # Logging configuration
    string_buffer = StringBuffer()

    # This filter will hide errors on papermill execution
    # def papermill_log_output_filter(record):
    #     return record.funcName == "log_output_message"

    def customize_logger_record(record):
        """Add notebook name to log records"""
        record.current_notebook = os.path.basename(input_path)
        return True

    default_log_format = (
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]"
        " %(message)s"
    )
    formatter = jsonlogger.JsonFormatter(default_log_format)
    # Handlers
    # Console
    stream_handler = logging.StreamHandler(string_buffer)
    stream_handler.setFormatter(formatter)
    # File
    papermill_logger = logging.getLogger("papermill")
    papermill_logger.setLevel(logging.INFO)
    papermill_logger.addHandler(stream_handler)
    # papermill_logger.addFilter(papermill_log_output_filter)
    papermill_logger.addFilter(customize_logger_record)

    # Run notebook
    def execute_notebook(input_path, output_path):
        try:
            pm.execute_notebook(
                input_path=input_path,
                output_path=output_path,
                log_output=True,
                progress_bar=False,
            )
        except Exception as error:
            papermill_logger.error(f"Execution error: {error}")

    execute_notebook(input_path, output_path)
    # Make DataFrame from logs
    log_contents = string_buffer.getvalue()
    dict_pattern = r"(\{[^{}]+\})"
    matches = re.findall(dict_pattern, log_contents)
    _df = None
    if matches:
        log_list = [json.loads(log) for log in matches]
        _df = pd.DataFrame(log_list)
    # TODO
    # Close buffer without error
    # string_buffer.close()
    return _df
