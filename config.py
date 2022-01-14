"""
Application configuration class
"""


class Config:
    CYCLE = 5
    TIME_ZONE = "America/Sao_Paulo"
    WORKFLOWS_CONFIG_PATH = "./samples/papermill"
    JOB_DATABASE_URL = "sqlite:///jobs.sqlite"
    WORKFLOWS_EXECUTION_DATABASE_URL = "test.db"
