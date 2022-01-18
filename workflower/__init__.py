import logging
import time

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.jobstores.base import JobLookupError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config

from workflower.loader import load_all

logger = logging.getLogger("workflower")


# TODO
# Make an workflow dependencies check event
def job_runs(event):
    if event.exception:
        logger.warning(f"Job: {event.job_id}, did not run: {event.exception}")
    else:
        logger.info(f"Job: {event.job_id}, successfully executed")


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
            logger.info("Checking workflows")
            if self.workflows:
                logger.info("Checking scheduled jobs")
                # This jobs were scheduled on past cycle
                scheduled_jobs = [
                    job[0].name
                    for job in [workflow.jobs for workflow in self.workflows]
                ]
                logger.info("Checking loaded jobs")
                # This jobs were loaded on most recent cycle
                loaded_jobs = [
                    job[0].name
                    for job in [workflow.jobs for workflow in workflows]
                ]
                logger.info("Checking removed jobs")
                # Get removed jobs, this will remove job's
                # file has been removed
                removed_jobs = [
                    job_name
                    for job_name in scheduled_jobs
                    if job_name not in loaded_jobs
                ]
                logger.info("Checking modified jobs")
                # Get modified jobs, this will remove job if has been modified
                # to reschedule it after
                for new_workflow in workflows:
                    # Modified workflows according to file modification time
                    modified_workflows = [
                        workflow
                        for workflow in self.workflows
                        if (new_workflow.name == workflow.name)
                        and (new_workflow.modified_at != workflow.modified_at)
                    ]
                    # Modified jobs according to workflow modification time
                    modified_jobs = [
                        job[0].name
                        for job in [
                            workflow.jobs for workflow in modified_workflows
                        ]
                    ]
                logger.info("Removing jobs jobs")
                # Remove deleted or modified jobs from scheduler
                jobs_to_remove = []
                if jobs_to_remove:
                    jobs_to_remove.extend(modified_jobs)
                    jobs_to_remove.extend(removed_jobs)
                    for job_id in jobs_to_remove:
                        logger.info(f"Removing: {removed_jobs}")
                        try:
                            self.scheduler.remove_job(job_id)
                        except JobLookupError:
                            logger.warning(
                                f"tried to remove {job_id}, "
                                "but it was not scheduled"
                            )

            # schedule jobs
            logger.info("Scheduling jobs")
            self.workflows = workflows
            for workflow in self.workflows:
                workflow.schedule_jobs(self.scheduler)
            logger.info(f"Sleeping {Config.CYCLE} seconds")
            time.sleep(Config.CYCLE)
