"""
Application configuration.
"""
import os


class Config:
    """
    Application configuration class.
    """

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    CYCLE = int(os.getenv("CYCLE", 60))
    TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
    WORKFLOWS_FILES_PATH = os.getenv(
        "WORKFLOWS_FILES_PATH", "./samples/workflows"
    )
    DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))
    APP_DATABASE_URL = os.getenv("APP_DATABASE_URL", "sqlite://")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOGGING_PATH = os.getenv(
        "LOGGING_PATH",
        os.path.join(
            DATA_DIR,
            "logs",
        ),
    )
    LOGGING_FILE = os.getenv("LOGGING_FILE", "log.log")
    ENVIRONMENTS_DIR = os.getenv(
        "ENVIRONMENTS_DIR",
        os.path.join(
            DATA_DIR,
            "environments",
        ),
    )
    KERNELS_SPECS_DIR = os.getenv(
        "KERNELS_SPECS_DIR",
        os.path.join(
            DATA_DIR,
            "kernel_specs",
        ),
    )
    PIP_INDEX_URL = os.getenv("PIP_INDEX_URL", None)
    PIP_TRUSTED_HOST = os.getenv("PIP_TRUSTED_HOST", None)
