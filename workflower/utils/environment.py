import json
import logging
import os
import platform
import subprocess
import uuid
import venv

from config import Config
from jupyter_client.kernelspecapp import KernelSpecManager

logger = logging.getLogger("workflower.utils.environment")


def create_venv(environments_dir, name, with_pip=True):
    """
    Create virtual environment.
    """
    logger.info("Creating virtual environment")
    env_path = os.path.join(environments_dir, name)
    logger.info(f"Virtual environment name: {env_path}")

    venv.create(env_path, system_site_packages=True, with_pip=with_pip)
    if platform.system() == "Windows":
        env_executable = os.path.join(env_path, "Scripts", "python")
    else:
        # Linux
        env_executable = os.path.join(env_path, "bin", "python")
    return env_path, env_executable


def create_and_install_kernel(
    environments_dir=Config.ENVIRONMENTS_DIR,
    kernel_specs_dir=Config.KERNELS_SPECS_DIR,
):
    # Create environment
    logger.info("Creating Kernel")
    kernel_name = str(uuid.uuid4())
    logger.info(f"Kernel name {kernel_name}")

    env_path, env_executable = create_venv(environments_dir, kernel_name)
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
    kernel_spec_folder = os.path.join(kernel_specs_dir, kernel_name)
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
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    return kernel_name, kernel_spec_folder, env_path
