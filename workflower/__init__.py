import logging
import time
from functools import reduce

import pandas as pd
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.jobstores.base import JobLookupError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config

from workflower.loader import load_all

logger = logging.getLogger("workflower")


class App:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.workflows = None
        self.jobs = None
        self.is_running = False

    def job_execution(self, event) -> None:
        if event.exception:
            logger.warning(
                f"Job: {event.job_id}, did not run: {event.exception}"
            )
        else:
            job = self.scheduler.get_job(event.job_id)
            if job:
                logger.info(f"Job: {event.job_id}, successfully executed")
                logger.debug(f"job nextrun {job.next_run_time}")

    def save_job_execution(self, event) -> None:
        logger.debug("Checking if should save job execution")
        if event.exception:
            return
        else:
            job = self.scheduler.get_job(event.job_id)
            if job:
                logger.debug(f"job id {job.id}")
                job_wrapper = [
                    scheduled_job
                    for scheduled_job in self.jobs
                    if scheduled_job.name == job.id
                ]
                if job_wrapper:
                    job_wrapper = job_wrapper[0]
                    logger.debug(f"Job uses: {job_wrapper.uses}")
                    return_value = event.retval
                    if isinstance(return_value, pd.DataFrame):
                        self.scheduler.add_job(
                            func=job_wrapper.save_execution,
                            kwargs=dict(dataframe=return_value),
                        )

    def run_dependency_job(self, event) -> None:
        logger.debug("Checking for dependency jobs")
        if event.exception:
            return
        else:
            job = self.scheduler.get_job(event.job_id)
            if job:
                logger.debug(f"job id {job.id}")
                job_wrapper = [
                    scheduled_job
                    for scheduled_job in self.jobs
                    if scheduled_job.depends_on == job.id
                ]
                logger.debug(f"dependency object: {job_wrapper}")
                if job_wrapper:
                    job_wrapper = job_wrapper[0]
                    logger.debug(
                        f"Dependency job {job_wrapper.name} triggered"
                    )
                    job_wrapper.schedule(self.scheduler)

    def setup(self) -> None:
        jobstores = {
            "default": SQLAlchemyJobStore(url=Config.JOB_DATABASE_URL),
        }
        executors = {
            "default": {"type": "threadpool", "max_workers": 20},
        }

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(
            self.job_execution, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )
        self.scheduler.add_listener(
            self.save_job_execution, EVENT_JOB_EXECUTED
        )
        self.scheduler.add_listener(
            self.run_dependency_job, EVENT_JOB_EXECUTED
        )
        self.scheduler.configure(
            jobstores=jobstores,
            executors=executors,
            timezone=Config.TIME_ZONE,
        )

    def run(self) -> None:
        self.scheduler.start()
        self.is_running = True
        while self.is_running:
            logger.info("Loading Workflows")
            workflows = load_all()
            jobs = reduce(
                lambda x, y: x + y,
                [workflow.jobs for workflow in workflows],
            )
            for workflow in workflows:
                logger.debug(
                    f"Found workflow: {workflow.name} - "
                    f"last modified at: {workflow.last_modified_at}"
                )
            # TODO
            # improve this ugly code
            # Update schedule if file is changed
            logger.info("Checking workflows")
            logger.info(f"Workflows Loaded {len(workflows)}")
            if self.workflows:
                for loaded_workflow in self.workflows:
                    logger.debug(
                        f"Stored workflow: {loaded_workflow.name} - "
                        f"last modified at: {loaded_workflow.last_modified_at}"
                    )
                logger.info(
                    f"Current scheduled workflows {len(self.workflows)}"
                )
                logger.info("Checking scheduled jobs")
                # This jobs were scheduled on past cycle
                scheduled_jobs = [job.name for job in self.jobs]
                logger.info("Checking loaded jobs")
                # This jobs were loaded on most recent cycle
                loaded_jobs = [job.name for job in jobs]
                logger.info("Checking removed jobs")
                # Get removed jobs, this will remove job's
                # file has been removed
                removed_jobs = [
                    job_name
                    for job_name in scheduled_jobs
                    if job_name not in loaded_jobs
                ]
                # Get modified jobs, this will remove job if has been modified
                # to reschedule it after
                modified_jobs = []
                for new_workflow in workflows:
                    # Modified workflows according to file modification time
                    modified_workflows = [
                        workflow
                        for workflow in self.workflows
                        if (new_workflow.name == workflow.name)
                        and (
                            new_workflow.last_modified_at
                            != workflow.last_modified_at
                        )
                    ]
                    # Modified jobs according to workflow modification time
                    if modified_workflows:
                        modified_jobs.extend(
                            [
                                job.name
                                for job in reduce(
                                    lambda x, y: x + y,
                                    [
                                        workflow.jobs
                                        for workflow in modified_workflows
                                    ],
                                )
                            ]
                        )
                logger.info("Removing jobs")
                # Remove deleted or modified jobs from scheduler
                logger.debug(f"_Removed jobs: {removed_jobs}")
                logger.debug(f"_Modified jobs: {modified_jobs}")
                jobs_to_remove = []
                if removed_jobs or modified_jobs:
                    logger.info(f"Removed jobs: {removed_jobs}")
                    logger.info(f"Modified jobs: {modified_jobs}")
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
            self.jobs = reduce(
                lambda x, y: x + y,
                [workflow.jobs for workflow in self.workflows],
            )
            for workflow in self.workflows:
                workflow.schedule_jobs(self.scheduler)
            logger.info(f"Sleeping {Config.CYCLE} seconds")
            time.sleep(Config.CYCLE)
