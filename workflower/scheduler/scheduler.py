import asyncio
import logging
import os
import threading

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


class Scheduler:
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
        Event.create(
            name="job_error",
            model="job",
            model_id=job.id,
            exception=event.exception,
        )

    def on_job_executed(self, event) -> None:
        logger.info(f"Job: {event.job_id}, successfully executed")
        job = Job.get_one(name=event.job_id)
        Event.create(
            name="job_executed",
            model="job",
            model_id=job.id,
            output=event.retval,
        )
        Job.update_next_run_time(event.job_id, self.scheduler)
        self.trigger_job_dependency(event)

    def trigger_job_dependency(self, event):
        """
        Trigger a job that depends on another.
        """
        logger.debug("Checking if need to trigger a dependency job")
        Job.trigger_dependencies(
            event.job_id, self.scheduler, job_return_value=event.retval
        )

    def setup(self) -> None:
        if not os.path.isdir(Config.ENVIRONMENTS_DIR):
            os.makedirs(Config.ENVIRONMENTS_DIR)

        if not os.path.isdir(Config.DATA_DIR):
            os.makedirs(Config.DATA_DIR)

        jobstores = {"default": SQLAlchemyJobStore(engine=database.engine)}
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

    async def run(self) -> None:
        """
        Run app.
        """
        self.scheduler.start()
        self.is_running = True
        logger.debug(f"STUCK THREADS {threading.enumerate()}")

        while self.is_running:
            logger.info("Loading Workflows")
            workflows_loader = Loader()
            workflows_loader.load_all()
            workflows = Workflow.get_all()
            logger.info(f"Workflows Loaded {len(workflows)}")
            Workflow.schedule_all_jobs(self.scheduler)
            logger.info(f"Sleeping {Config.CYCLE} seconds")
            await asyncio.sleep(Config.CYCLE)

    def stop(self):
        logger.info("Stopping App")
        self.is_running = False
        database.close()
