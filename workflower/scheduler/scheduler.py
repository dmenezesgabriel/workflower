import logging
import os

from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_REMOVED,
)
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from workflower.config import Config
from workflower.models.base import database
from workflower.models.event import Event

logger = logging.getLogger("workflower.app")


class SchedulerService:
    """
    Scheduler service.
    """

    def __init__(self):
        self._scheduler = BackgroundScheduler()
        self.is_running = False

    @property
    def scheduler(self):
        return self._scheduler

    def on_job_executed(self, event) -> None:
        """
        On job executed event.
        """
        Event.job_executed(event, self._scheduler)

    def create_default_directories(self) -> None:
        """
        Create application default configuration directories.
        """
        if not os.path.isdir(Config.ENVIRONMENTS_DIR):
            os.makedirs(Config.ENVIRONMENTS_DIR)

        if not os.path.isdir(Config.DATA_DIR):
            os.makedirs(Config.DATA_DIR)

    def setup_event_actions(self, scheduler) -> None:
        """
        Add event listeners
        """
        event_actions = [
            {"func": Event.job_added, "event": EVENT_JOB_ADDED},
            {"func": self.on_job_executed, "event": EVENT_JOB_EXECUTED},
            {"func": Event.job_error, "event": EVENT_JOB_ERROR},
            {"func": Event.job_removed, "event": EVENT_JOB_REMOVED},
        ]
        for event_action in event_actions:
            scheduler.add_listener(
                event_action["func"],
                event_action["event"],
            )

    def setup(self) -> None:
        """
        Setup general app configuration.
        """
        self.create_default_directories()
        jobstores = {
            "default": SQLAlchemyJobStore(engine=database.engine),
        }
        executors = {
            "default": {
                "type": "threadpool",
                "max_workers": 20,
            },
        }
        self._scheduler = BackgroundScheduler()
        self.setup_event_actions(self._scheduler)
        self._scheduler.configure(
            jobstores=jobstores,
            executors=executors,
            timezone=Config.TIME_ZONE,
        )

    def init(self):
        """
        Initialize app.
        """
        database.connect()

    async def run(self) -> None:
        """
        Run app.
        """
        self._scheduler.start()
        self.is_running = True

    def stop(self):
        """
        Stop app.
        """
        logger.info("Stopping App")
        self.is_running = False
        database.close()
