import logging

from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_REMOVED,
)
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from workflower.adapters.sqlalchemy.setup import Session
from workflower.adapters.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from workflower.application.event.commands import CreateEventCommand
from workflower.application.job.commands import (
    GetDependencyTriggerJobsCommand,
    ScheduleJobCommand,
    UpdateNextRunTimeCommand,
)
from workflower.config import Config

logger = logging.getLogger("workflower.scheduler")


class WorkflowScheduler:
    """
    Scheduler service.
    """

    def __init__(self, engine) -> None:
        self._scheduler = BackgroundScheduler()
        self._is_running = False
        self.engine = engine
        self._init()

    @property
    def scheduler(self):
        return self._scheduler

    @property
    def is_running(self):
        return self._is_running

    def on_job_added(self, event) -> None:
        session = Session()
        uow = SqlAlchemyUnitOfWork(session)
        with uow:
            command = CreateEventCommand(
                uow,
                name="job_added",
                model="job",
                model_id=event.job_id,
                exception=None,
                output=None,
            )
            command.execute()

    def on_job_removed(self, event) -> None:
        session = Session()
        uow = SqlAlchemyUnitOfWork(session)
        with uow:
            command = CreateEventCommand(
                uow,
                name="job_removed",
                model="job",
                model_id=event.job_id,
                exception=None,
                output=None,
            )
            command.execute()

    def on_job_executed(self, event) -> None:
        """
        On job executed event.
        """
        session = Session()
        uow = SqlAlchemyUnitOfWork(session)
        with uow:
            create_event_command = CreateEventCommand(
                uow,
                name="job_executed",
                model="job",
                model_id=event.job_id,
                exception=None,
                output=event.retval,
            )
            create_event_command.execute()
            update_next_runtime_command = UpdateNextRunTimeCommand(
                uow, event.job_id, self.scheduler
            )
            update_next_runtime_command.execute()
            get_dependency_jobs_command = GetDependencyTriggerJobsCommand(
                uow, event.job_id, event.retval
            )
            dependency_jobs = get_dependency_jobs_command.execute()
            for dependency_job in dependency_jobs:
                schedule_job_command = ScheduleJobCommand(
                    uow,
                    dependency_job.id,
                    self.scheduler,
                    job_return_value=event.retval,
                )
                schedule_job_command.execute()

    def on_job_error(self, event) -> None:
        session = Session()
        uow = SqlAlchemyUnitOfWork(session)
        with uow:
            command = CreateEventCommand(
                uow,
                name="job_error",
                model="job",
                model_id=event.job_id,
                exception=event.exception,
                output=None,
            )
            command.execute()

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
            "default": SQLAlchemyJobStore(engine=self.engine),
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
