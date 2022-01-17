import logging
import time

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.jobstores.base import JobLookupError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config

from workflower.loader import load_all

log_format = (
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d]"
    " %(message)s"
)
logging.basicConfig(
    encoding="utf-8",
    level=logging.INFO,
    format=log_format,
)
logger = logging.getLogger(__name__)


# TODO
# Make an workflow dependencies check event
def job_runs(event):
    if event.exception:
        logger.warning("Job did not run")
    else:
        logger.info("Job successfully executed")


def job_return_val(event):
    return event.retval


class App:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.workflows = None

    def setup(self):
        jobstores = {
            "default": SQLAlchemyJobStore(url=Config.JOB_DATABASE_URL),
        }
        executors = {
            "default": {"type": "threadpool", "max_workers": 20},
        }

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(
            job_runs, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )
        self.scheduler.add_listener(job_return_val, EVENT_JOB_EXECUTED)
        self.scheduler.configure(
            jobstores=jobstores,
            executors=executors,
            timezone=Config.TIME_ZONE,
        )

    def run(self):
        self.scheduler.start()
        while True:
            logger.info("Loading Workflows")
            workflows = load_all()
            # TODO
            # improve this ugly code
            # Update schedule if file is changed
            logger.info("Unscheduling removed workflows")
            if self.workflows:
                scheduled_jobs = [
                    job[0].name
                    for job in [workflow.jobs for workflow in self.workflows]
                ]
                loaded_jobs = [
                    job[0].name
                    for job in [workflow.jobs for workflow in workflows]
                ]
                removed_jobs = [
                    job_name
                    for job_name in scheduled_jobs
                    if job_name not in loaded_jobs
                ]
                print(removed_jobs)
                for job_id in removed_jobs:
                    logger.info(f"Removing: {removed_jobs}")
                    try:
                        self.scheduler.remove_job(job_id)
                    except JobLookupError:
                        logger.debug(f"{removed_jobs} was not scheduled")
            # schedule jobs
            self.workflows = workflows
            for workflow in self.workflows:
                workflow.schedule_jobs(self.scheduler)
            logger.info(f"Sleeping {Config.CYCLE} seconds")
            time.sleep(Config.CYCLE)
