import logging
import shutil

import pandas as pd
from workflower.operators.operator import BaseOperator
from workflower.utils.environment import create_and_install_kernel

import papermill as pm

logger = logging.getLogger("papermill")


class PapermillOperator(BaseOperator):
    @staticmethod
    def run_notebook(input_path, output_path) -> pd.DataFrame:
        """
        Run notebook.
        """

        # File

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
                logger.error(f"Execution error: {error}")
            finally:
                if env_name is not None:
                    shutil.rmtree(path=env_name)
                if kernel_spec_folder is not None:
                    shutil.rmtree(path=kernel_spec_folder)

        execute_notebook(input_path, output_path)
