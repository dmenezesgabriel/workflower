import logging
import time

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
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
    level=logging.DEBUG,
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
            print("Loading Workflows")
            # TODO
            # Move to a modules loader
            workflows = load_all()
            for workflow in workflows:
                workflow.schedule_jobs(self.scheduler)
            self.scheduler.print_jobs()
            time.sleep(Config.CYCLE)
