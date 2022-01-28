import logging
import shutil

from workflower.operators.operator import BaseOperator
from workflower.utils.environment import create_and_install_kernel

import papermill as pm

logger = logging.getLogger("workflower.operators.papermill")


class PapermillOperator(BaseOperator):
    @staticmethod
    def execute(
        input_path,
        output_path,
        create_env=True,
        kernel_name=None,
        kernel_spec_folder=None,
        env_path=None,
        environments_dir=None,
        kernel_specs_dir=None,
        pip_index_url=None,
        pip_trusted_host=None,
        *args,
        **kwargs,
    ):
        """
        Run notebook with papermill.
        """
        if create_env:
            (
                kernel_name,
                kernel_spec_folder,
                env_path,
            ) = create_and_install_kernel(
                environments_dir,
                kernel_specs_dir,
                pip_index_url,
                pip_trusted_host,
            )

        try:
            notebook = pm.execute_notebook(
                input_path=input_path,
                output_path=output_path,
                log_output=True,
                progress_bar=False,
                kernel_name=kernel_name,
                request_save_on_cell_execute=True,
            )
            return str(notebook)
        except Exception as error:
            logger.error(f"Papermill execution error: {error}")
        finally:
            if env_path is not None:
                shutil.rmtree(path=env_path)
            if kernel_spec_folder is not None:
                shutil.rmtree(path=kernel_spec_folder)
