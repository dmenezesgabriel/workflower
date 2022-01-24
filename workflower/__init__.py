import logging
import os
import time

from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_REMOVED,
)
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config

from workflower.loader import Loader
from workflower.models.base import database
from workflower.models.event import Event
from workflower.models.job import Job
from workflower.models.workflow import Workflow

logger = logging.getLogger("workflower.app")


class App:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False

    def on_job_added(self, event):
        job = Job.get_one(name=event.job_id)
        Event.create(name="job_added", model="job", model_id=job.id)

    def on_job_removed(self, event):
        job = Job.get_one(name=event.job_id)
        Event.create(name="job_removed", model="job", model_id=job.id)

    def on_job_error(self, event) -> None:
        job = Job.get_one(name=event.job_id)
        event_object = Event.create(
            name="job_error", model="job", model_id=job.id
        )
        if event.exception:
            logger.warning(
                f"Job: {event.job_id}, did not run: {event.exception}"
            )
            Event.update(id=event_object.id, exception=event.exception)

    def on_job_executed(self, event) -> None:
        logger.info(f"Job: {event.job_id}, successfully executed")
        job = Job.get_one(name=event.job_id)
        Event.create(
            name="job_executed",
            model="job",
            model_id=job.id,
            output=event.retval,
        )
        self.trigger_job_dependency(event)

    def trigger_job_dependency(self, event):
        """
        Trigger a job that depends on another.
        """
        logger.debug("Checking if need to trigger a dependency job")
        Job.trigger_dependencies(event.job_id, self.scheduler)

    def setup(self) -> None:
        if not os.path.isdir(Config.ENVIRONMENTS_FOLDER):
            os.makedirs(Config.ENVIRONMENTS_FOLDER)

        jobstores = {
            "default": SQLAlchemyJobStore(url=Config.JOB_DATABASE_URL),
        }
        executors = {
            "default": {"type": "threadpool", "max_workers": 20},
        }

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(self.on_job_added, EVENT_JOB_ADDED)
        self.scheduler.add_listener(self.on_job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self.on_job_error, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self.on_job_removed, EVENT_JOB_REMOVED)

        self.scheduler.configure(
            jobstores=jobstores,
            executors=executors,
            timezone=Config.TIME_ZONE,
        )

    def init(self):
        database.connect()

    def run(self) -> None:
        """
        Run app.
        """
        self.scheduler.start()
        self.is_running = True
        while self.is_running:
            logger.info("Loading Workflows")
            workflows_loader = Loader()
            workflows_loader.load_all()
            workflows = Workflow.get_all()
            logger.info(f"Workflows Loaded {len(workflows)}")
            Workflow.schedule_all_jobs(self.scheduler)
            logger.info(f"Sleeping {Config.CYCLE} seconds")
            time.sleep(Config.CYCLE)

    def stop(self):
        self.is_running = False
        self.scheduler.shutdown()
        time.sleep(5)
        database.close()
