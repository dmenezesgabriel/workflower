import json
import os
import platform
import subprocess
import uuid
import venv

import pandas as pd
from config import Config
from jupyter_client.kernelspecapp import KernelSpecManager


def create_and_install_kernel():
    # Create environment

    kernel_name = str(uuid.uuid4())
    env_name = f"{Config.ENVIRONMENTS_FOLDER}/{kernel_name}"
    venv.create(env_name, system_site_packages=True, with_pip=True)
    if platform.system() == "Windows":
        env_executable = os.path.join(env_name, "Scripts", "python")
    else:
        # Linux
        env_executable = os.path.join(env_name, "bin", "python")

    # Create kernel spec
    kernel_spec = {
        "argv": [
            env_executable,
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}",
        ],
        "display_name": "Python 3",
        "language": "python",
    }
    kernel_spec_folder = os.path.join(Config.KERNELS_SPECS_PATH, kernel_name)
    kernel_spec_file = os.path.join(kernel_spec_folder, "kernel.json")

    # Create kernel spec folder
    if not os.path.exists(os.path.dirname(kernel_spec_file)):
        try:
            os.makedirs(os.path.dirname(kernel_spec_file))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(kernel_spec_file, mode="w", encoding="utf-8") as f:
        json.dump(kernel_spec, f)

    # Install kernel
    kernel_spec_manager = KernelSpecManager()
    kernel_spec_manager.install_kernel_spec(
        source_dir=kernel_spec_folder, kernel_name=kernel_name
    )
    subprocess.check_output(
        [env_executable, "-m", "pip", "install", "ipykernel"]
    )
    return kernel_name, kernel_spec_folder, env_name


def run_notebook(input_path, output_path) -> pd.DataFrame:
    import json
    import logging
    import os
    import re
    import shutil
    from io import StringIO as StringBuffer

    import pandas as pd

    # TODO
    # limit workbook output log with custom filter
    from pythonjsonlogger import jsonlogger

    import papermill as pm

    # Logging configuration
    string_buffer = StringBuffer()

    # def papermill_log_output_filter(record):
    #     return record.funcName == "log_output_message"

    def customize_logger_record(record):
        """Add notebook name to log records"""
        record.current_notebook = os.path.basename(input_path)
        return True

    def clean_record(record):
        """Add notebook name to log records"""
        record.msg = record.msg[:250]
        record.msg = [
            character
            for character in record.msg
            if character.isalnum() or character == " "
        ]

        return True

    default_log_format = (
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]"
        " %(message)s"
    )
    formatter = jsonlogger.JsonFormatter(default_log_format)
    # Handlers
    # Console
    buffer_handler = logging.StreamHandler(string_buffer)
    # stream_handler = logging.StreamHandler()
    # stream_handler.setFormatter(formatter)
    buffer_handler.setFormatter(formatter)
    # File
    papermill_logger = logging.getLogger("papermill")
    papermill_logger.setLevel(logging.INFO)
    papermill_logger.addHandler(buffer_handler)
    # papermill_logger.addHandler(stream_handler)

    papermill_logger.addFilter(customize_logger_record)
    # papermill_logger.addFilter(papermill_log_output_filter)
    # papermill_logger.addFilter(clean_record)

    # Run notebook
    def execute_notebook(input_path, output_path):
        kernel_name, kernel_spec_folder, env_name = create_and_install_kernel()

        try:
            pm.execute_notebook(
                input_path=input_path,
                output_path=output_path,
                log_output=True,
                progress_bar=False,
                kernel_name=kernel_name,
            )
        except Exception as error:
            papermill_logger.error(f"Execution error: {error}")
        finally:
            if env_name is not None:
                shutil.rmtree(path=env_name)
            if kernel_spec_folder is not None:
                shutil.rmtree(path=kernel_spec_folder)

    execute_notebook(input_path, output_path)
    # Make DataFrame from logs
    log_contents = string_buffer.getvalue().replace("\n", " ")
    dict_pattern = r'(\{"[^{}]+"\})'
    matches = re.findall(dict_pattern, log_contents)
    _df = None
    if matches:
        log_list = []
        for log in matches:
            try:
                log_dict = json.loads(log)
                log_list.append(log_dict)
            except Exception:
                continue
        _df = pd.DataFrame(log_list)
    # TODO
    # Close buffer without error
    # string_buffer.close()
    return _df
