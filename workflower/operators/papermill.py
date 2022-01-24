import json
import logging
import os
import platform
import shutil
import subprocess
import uuid
import venv
from logging.handlers import RotatingFileHandler

import pandas as pd
from config import Config
from jupyter_client.kernelspecapp import KernelSpecManager
from workflower.operators.operator import BaseOperator
from workflower.utils.file import get_file_name

import papermill as pm


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
            if exc.errno != exc.errno.EEXIST:
                raise

    with open(kernel_spec_file, mode="w", encoding="utf-8") as f:
        json.dump(kernel_spec, f)

    # Install kernel
    kernel_spec_manager = KernelSpecManager()
    kernel_spec_manager.install_kernel_spec(
        source_dir=kernel_spec_folder, kernel_name=kernel_name
    )
    subprocess.run(
        [env_executable, "-m", "pip", "-q", "install", "ipykernel"],
        capture_output=False,
    )
    return kernel_name, kernel_spec_folder, env_name


class PapermillOperator(BaseOperator):
    @staticmethod
    def run_notebook(input_path, output_path) -> pd.DataFrame:
        """
        Run notebook.
        """

        # Logging configuration
        default_log_format = (
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]"
            " %(message)s"
        )
        formatter = logging.Formatter(default_log_format)
        # Handlers
        log_file_path = os.path.join(
            Config.LOGGING_PATH, f"{get_file_name(input_path)}.log"
        )
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=50000,
            backupCount=3,
        )
        file_handler.setFormatter(formatter)
        # File
        papermill_logger = logging.getLogger("papermill")
        papermill_logger.setLevel(logging.INFO)
        papermill_logger.addHandler(file_handler)

        # Run notebook
        def execute_notebook(input_path, output_path):
            (
                kernel_name,
                kernel_spec_folder,
                env_name,
            ) = create_and_install_kernel()

            try:
                pm.execute_notebook(
                    input_path=input_path,
                    output_path=output_path,
                    log_output=True,
                    progress_bar=False,
                    kernel_name=kernel_name,
                    request_save_on_cell_execute=True,
                )
            except Exception as error:
                papermill_logger.error(f"Execution error: {error}")
            finally:
                if env_name is not None:
                    shutil.rmtree(path=env_name)
                if kernel_spec_folder is not None:
                    shutil.rmtree(path=kernel_spec_folder)

        execute_notebook(input_path, output_path)
