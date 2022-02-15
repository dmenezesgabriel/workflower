"""
Application configuration.
"""
import os


class Config:
    """
    Application configuration class.
    """

    # ======================================================================= #
    # Application base directory
    # ======================================================================= #
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # ======================================================================= #
    # Application run cycle
    # ======================================================================= #
    CYCLE = int(os.getenv("CYCLE", 60))
    # ======================================================================= #
    # Application time zone
    # ======================================================================= #
    TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
    # ======================================================================= #
    # Workflow yaml files location
    # ======================================================================= #
    WORKFLOWS_FILES_PATH = os.getenv(
        "WORKFLOWS_FILES_PATH", "./samples/workflows"
    )
    # ======================================================================= #
    # Default application data directory
    # ======================================================================= #
    DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))
    # ======================================================================= #
    # Database Directory
    # ======================================================================= #
    DEFAULT_DATABASE_DIR = os.path.join(DATA_DIR, "app-dev.sqlite")
    APP_DATABASE_URL = os.getenv(
        "APP_DATABASE_URL", f"sqlite:///{DEFAULT_DATABASE_DIR}"
    )
    # ======================================================================= #
    # Logging default configuration
    # ======================================================================= #
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOGGING_PATH = os.getenv(
        "LOGGING_PATH",
        os.path.join(
            DATA_DIR,
            "logs",
        ),
    )
    LOGGING_FILE = os.getenv("LOGGING_FILE", "log.log")
    LOGGING_FILE_MAX_BYTES = int(os.getenv("LOGGING_FILE_MAX_BYTES", 90000))
    LOGGING_FILE_BACKUP_COUNT = int(os.getenv("LOGGING_FILE_BACKUP_COUNT", 1))
    # ======================================================================= #
    # Virtual environments and jupyter kernels default directories
    # ======================================================================= #
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
    # ======================================================================= #
    # Pip default options
    # ======================================================================= #
    PIP_INDEX_URL = os.getenv("PIP_INDEX_URL", None)
    PIP_TRUSTED_HOST = os.getenv("PIP_TRUSTED_HOST", None)
