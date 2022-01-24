import json
import os
import platform
import subprocess
import uuid
import venv

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
