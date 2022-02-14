import logging

from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_REMOVED,
)
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from workflower.config import Config
from workflower.database import DatabaseManager
from workflower.models.base import database
from workflower.models.event import Event

logger = logging.getLogger("workflower.app")


class SchedulerService:
    """
    Scheduler service.
    """

    def __init__(self, database: DatabaseManager = database) -> None:
        self._scheduler = BackgroundScheduler()
        self._is_running = False
        self._database = database
        self._init()

    @property
    def scheduler(self):
        return self._scheduler

    @property
    def is_running(self):
        return self._is_running

    def on_job_added(self, event) -> None:
        with self._database.session_scope() as session:
            Event.job_added(session, event)

    def on_job_removed(self, event) -> None:
        with self._database.session_scope() as session:
            Event.job_removed(session, event)

    def on_job_executed(self, event) -> None:
        """
        On job executed event.
        """
        with self._database.session_scope() as session:
            Event.job_executed(session, event, self._scheduler)

    def on_job_error(self, event) -> None:
        with self._database.session_scope() as session:
            Event.job_error(session, event)

    def setup_event_actions(self, scheduler) -> None:
        """
        Add event listeners
        """
        logger.info("Setting Up Scheduler Service Events")
        event_actions = [
            {"func": self.on_job_added, "event": EVENT_JOB_ADDED},
            {"func": self.on_job_executed, "event": EVENT_JOB_EXECUTED},
            {"func": self.on_job_error, "event": EVENT_JOB_ERROR},
            {"func": self.on_job_removed, "event": EVENT_JOB_REMOVED},
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
        logger.info("Setting Up Scheduler Service")
        jobstores = {
            "default": SQLAlchemyJobStore(engine=self._database.engine),
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

    def _init(self):
        """
        Initialize app.
        """
        logger.info("Initializing Scheduler Service")
        self.setup()

    def start(self) -> None:
        """
        Run app.
        """
        logger.info("Starting Scheduler Service")
        self._scheduler.start()
        self._is_running = True

    def stop(self):
        """
        Stop app.
        """
        logger.info("Stopping Scheduler Service")
        self._is_running = False
