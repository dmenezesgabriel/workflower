"""
Application configuration class
"""


class Config:
    CYCLE = 5
    WORKFLOWS_CONFIG_PATH = "./samples"
    JOB_DATABASE_URL = "sqlite:///jobs.sqlite"
    WORKFLOWS_EXECUTION_DATABASE_URL = "test.db"
