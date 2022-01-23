"""
Application configuration class
"""
import os


class Config:
    CYCLE = int(os.getenv("CYCLE", 60))
    TIME_ZONE = os.getenv("TIME_ZONE")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENTS_FOLDER = os.getenv("ENVIRONMENTS_FOLDER")
    KERNELS_SPECS_PATH = os.getenv("KERNELS_SPECS_PATH")
    LOGGING_PATH = os.getenv("LOGGING_PATH")
    LOGGING_FILE = os.getenv("LOGGING_FILE")
    WORKFLOWS_FILES_PATH = os.getenv("WORKFLOWS_FILES_PATH")
    APP_DATABASE_URL = os.getenv("APP_DATABASE_URL")
    JOB_DATABASE_URL = os.getenv("JOB_DATABASE_URL")
    WORKFLOWS_EXECUTION_DATABASE_URL = os.getenv(
        "WORKFLOWS_EXECUTION_DATABASE_URL"
    )
