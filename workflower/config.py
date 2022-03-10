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
    DATABASE_BACKUP_DEFAULT_DIR = os.path.join(DATA_DIR, "app-backup.sqlite")
    APP_DATABASE_BACKUP_URL = os.getenv(
        "APP_DATABASE_BACKUP_URL", DATABASE_BACKUP_DEFAULT_DIR
    )
    SQLITE_DATABASE_DUMP_PATH = os.getenv(
        "SQLITE_DATABASE_DUMP_PATH",
        os.path.join(
            DATA_DIR,
            "dump.sql",
        ),
    )
    # ======================================================================= #
    # Logging default configuration
    # ======================================================================= #
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOGGING_PATH = os.getenv(
        "LOGGING_PATH",
        os.path.join(
            DATA_DIR,
            "log",
        ),
    )
    CSV_LOGGING_PATH = os.getenv(
        "CSV_LOGGING_PATH",
        os.path.join(
            DATA_DIR,
            "log",
        ),
    )
    LOGGING_FILE = os.getenv("LOGGING_FILE", "log.log")
    LOGGING_FILE_MAX_BYTES = int(os.getenv("LOGGING_FILE_MAX_BYTES", 4096))
    LOGGING_FILE_BACKUP_COUNT = int(os.getenv("LOGGING_FILE_BACKUP_COUNT", 10))
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
    # ======================================================================= #
    # Pip default options
    # ======================================================================= #
    ALTERYX_ENGINE_PATH = os.getenv(
        "ALTERYX_ENGINE_PATH",
        "c:/Program Files/Alteryx/bin/AlteryxEngineCmd.exe",
    )


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass


class TestConfig(Config):
    APP_DATABASE_URL = "sqlite://"


class ConfigurationFactory:
    configuration_dict = dict(
        development=DevelopmentConfig,
        production=ProductionConfig,
        test=TestConfig,
    )

    @classmethod
    def get_config(cls, config_name):
        return cls.configuration_dict[config_name]
