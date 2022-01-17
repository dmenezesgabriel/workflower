"""
Application configuration class
"""
import os


class Config:
    DEBUG = os.getenv("DEBUG")
    TESTING = os.getenv("TESTING")
    DEVELOPMENT = os.getenv("DEVELOPMENT")
    CYCLE = int(os.getenv("CYCLE"))
    TIME_ZONE = os.getenv("TIME_ZONE")
    LOGGING_FILE = os.getenv("LOGGING_FILE")
    WORKFLOWS_CONFIG_PATH = os.getenv("WORKFLOWS_CONFIG_PATH")
    JOB_DATABASE_URL = os.getenv("JOB_DATABASE_URL")
    WORKFLOWS_EXECUTION_DATABASE_URL = os.getenv(
        "WORKFLOWS_EXECUTION_DATABASE_URL"
    )
