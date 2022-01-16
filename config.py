"""
Application configuration class
"""


class Config:
    DEBUG = False
    TESTING = False
    CYCLE = 5
    TIME_ZONE = "America/Sao_Paulo"
    WORKFLOWS_CONFIG_PATH = "./samples/workflows"
    JOB_DATABASE_URL = "sqlite:///jobs.sqlite"
    WORKFLOWS_EXECUTION_DATABASE_URL = "sqlite:///workflower.db"


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    JOB_DATABASE_URL = "sqlite:///jobs-dev.sqlite"
    WORKFLOWS_EXECUTION_DATABASE_URL = "sqlite:///workflower-dev.db"


class TestingConfig(Config):
    TESTING = True
    JOB_DATABASE_URL = "sqlite:///jobs-test.sqlite"
    WORKFLOWS_EXECUTION_DATABASE_URL = "sqlite:///workflower-test.db"
