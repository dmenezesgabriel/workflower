import logging
import os
import shutil
import subprocess
import traceback
import uuid

from workflower.operators.operator import BaseOperator
from workflower.utils.environment import create_venv

logger = logging.getLogger("workflower.operators.python")


class PythonOperator(BaseOperator):
    @staticmethod
    def execute(
        script_path=None,
        code=None,
        requirements_path=None,
        env_path=None,
        pip_index_url=None,
        pip_trusted_host=None,
        environments_dir=None,
        *args,
        **kwargs,
    ):
        """
        Run python with papermill.
        """
        output = {"logs": []}

        venv_name = str(uuid.uuid4())
        env_path, env_executable = create_venv(
            venv_name, environments_dir=environments_dir
        )

        output.update(dict(env_executable=env_executable))

        if requirements_path:
            if not os.path.isfile(requirements_path):
                logger.warning("Invalid requirements file path")
            pip_install_args = [
                env_executable,
                "-m",
                "pip",
                "-q",
                "install",
                "-r",
                requirements_path,
            ]
            output.update(dict(requirements_path=requirements_path))

            if pip_index_url:
                pip_install_args.append(f"--index-url={pip_index_url}")
            if pip_trusted_host:
                pip_install_args.append(f"--trusted-host={pip_trusted_host}")

            subprocess.run(
                pip_install_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

        run_python_args = [env_executable]

        #  Run script
        if script_path:
            logger.info(f"Running python script: {script_path}")
            run_python_args.append(script_path)
            output.update(dict(script_path=script_path))

            # Get output from previous job
            if "job_return_value" in kwargs:
                run_python_args.append(kwargs["job_return_value"])

        elif code:
            logger.info(f"Running python code: {code}")
            run_python_args.append("-c")
            run_python_args.append(code)
            output.update(dict(code=code))

        try:
            process = subprocess.Popen(
                run_python_args,
                stdout=subprocess.PIPE,
            )

            # Capture logs if exists
            with process.stdout:
                try:
                    for line in iter(process.stdout.readline, b""):

                        decoded_line = line.decode(
                            "utf-8", errors="ignore"
                        ).rstrip()
                        logger.info(decoded_line)
                        output["logs"].append({"message": decoded_line})
                except subprocess.CalledProcessError as e:
                    logger.error(f"{str(e)}")
            return str(output)
        except Exception:
            logger.error(f"Python execution error: {traceback.format_exc()}")
            return str(output)
        finally:
            if env_path is not None:
                shutil.rmtree(path=env_path)
