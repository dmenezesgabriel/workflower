"""
Job class.
"""

import logging

import pandas as pd
import sqlalchemy
from apscheduler.jobstores.base import ConflictingIdError
from config import Config

logger = logging.getLogger("workflower.job")


class JobWrapper:
    def __init__(self, name, uses=None, definition=None, depends_on=None):
        self.name = name
        self.uses = uses
        self.definition = definition
        self.depends_on = depends_on
        self.job = None

    def schedule(self, scheduler) -> None:
        """
        Schedule a job in apscheduler
        """
        job_id = self.definition["id"]
        logger.debug(f"scheduling {job_id}")
        logger.debug(self.definition)
        try:
            self.job = scheduler.add_job(**self.definition)
        except ConflictingIdError:
            logger.warning(f"{job_id}, already scheduled, skipping.")
        except ValueError as error:
            # If someone set an invalid date value it will lead
            # to this exception
            logger.error(f"Value error: {error}")
        except Exception as error:
            logger.error(f"Error: {error}")

    def save_execution(self, dataframe: pd.DataFrame):
        engine = sqlalchemy.create_engine(
            Config.WORKFLOWS_EXECUTION_DATABASE_URL
        )
        connection = engine.raw_connection()
        if self.uses == "papermill":
            dataframe.to_sql(
                con=connection, name="papermill_executions", if_exists="append"
            )
        if self.uses == "alteryx":
            dataframe.to_sql(
                con=connection, name="alteryx_executions", if_exists="append"
            )
        connection.close()
