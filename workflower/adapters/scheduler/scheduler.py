import logging

from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MAX_INSTANCES,
    EVENT_JOB_MISSED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_SUBMITTED,
)
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import scoped_session, sessionmaker
from workflower.adapters.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from workflower.application.event.commands import CreateEventCommand
from workflower.application.job.commands import (
    ChangeJobStatusCommand,
    GetDependencyTriggerJobsCommand,
    ScheduleJobCommand,
    UpdateNextRunTimeCommand,
)
from workflower.config import Config

logger = logging.getLogger("workflower.scheduler")


class WorkflowScheduler:
    """
    Scheduler services.
    """

    def __init__(self, engine) -> None:
        self._scheduler = BackgroundScheduler()
        self._is_running = False
        self.engine = engine
        self._init()

    def _session(self):
        return scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
            )
        )

    @property
    def scheduler(self):
        return self._scheduler

    @property
    def is_running(self):
        return self._is_running

    def on_job_added(self, event) -> None:
        session = self._session()
        uow = SqlAlchemyUnitOfWork(session)
        create_event_command = CreateEventCommand(
            uow,
            name="job_added",
            model="job",
            model_id=event.job_id,
            exception=None,
            output=None,
        )
        create_event_command.execute()
        change_job_status_command = ChangeJobStatusCommand(
            uow, event.job_id, "added"
        )
        change_job_status_command.execute()

    def on_job_missed(self, event) -> None:
        session = self._session()
        uow = SqlAlchemyUnitOfWork(session)
        create_event_command = CreateEventCommand(
            uow,
            name="job_missed",
            model="job",
            model_id=event.job_id,
            exception=None,
            output=None,
        )
        create_event_command.execute()
        change_job_status_command = ChangeJobStatusCommand(
            uow, event.job_id, "missed"
        )
        change_job_status_command.execute()

    def on_job_max_instances(self, event) -> None:
        session = self._session()
        uow = SqlAlchemyUnitOfWork(session)
        create_event_command = CreateEventCommand(
            uow,
            name="job_max_instances",
            model="job",
            model_id=event.job_id,
            exception=None,
            output=None,
        )
        create_event_command.execute()
        logger.warning(f"Job{event.job_id} has reached max instances")

    def on_job_submitted(self, event) -> None:
        session = self._session()
        uow = SqlAlchemyUnitOfWork(session)
        create_event_command = CreateEventCommand(
            uow,
            name="job_submitted",
            model="job",
            model_id=event.job_id,
            exception=None,
            output=None,
        )
        create_event_command.execute()
        change_job_status_command = ChangeJobStatusCommand(
            uow, event.job_id, "submitted"
        )
        change_job_status_command.execute()

    def on_job_removed(self, event) -> None:
        session = self._session()
        uow = SqlAlchemyUnitOfWork(session)
        with uow:
            create_event_command = CreateEventCommand(
                uow,
                name="job_removed",
                model="job",
                model_id=event.job_id,
                exception=None,
                output=None,
            )
            create_event_command.execute()
            change_job_status_command = ChangeJobStatusCommand(
                uow, event.job_id, "removed"
            )
            change_job_status_command.execute()

    def on_job_executed(self, event) -> None:
        """
        On job executed event.
        """
        session = self._session()
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
            change_job_status_command = ChangeJobStatusCommand(
                uow, event.job_id, "executed"
            )
            change_job_status_command.execute()
            create_event_command.execute()
            update_next_runtime_command = UpdateNextRunTimeCommand(
                uow, event.job_id, self.scheduler
            )
        with uow:
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
                change_dependency_job_status_command = ChangeJobStatusCommand(
                    uow, dependency_job.id, "scheduled"
                )
                change_dependency_job_status_command.execute()

    def on_job_error(self, event) -> None:
        session = self._session()
        uow = SqlAlchemyUnitOfWork(session)
        with uow:
            create_event_command = CreateEventCommand(
                uow,
                name="job_error",
                model="job",
                model_id=event.job_id,
                exception=event.exception,
                output=None,
            )
            create_event_command.execute()
            change_job_status_command = ChangeJobStatusCommand(
                uow, event.job_id, "error"
            )
            change_job_status_command.execute()

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
            {"func": self.on_job_submitted, "event": EVENT_JOB_SUBMITTED},
            {"func": self.on_job_missed, "event": EVENT_JOB_MISSED},
            {
                "func": self.on_job_max_instances,
                "event": EVENT_JOB_MAX_INSTANCES,
            },
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
