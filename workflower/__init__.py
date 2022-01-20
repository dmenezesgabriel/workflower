import logging
import os
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

    def trigger_job_dependency(self, event):
        """
        Trigger a job that depends on another.
        """
        logger.debug("Checking if need to trigger a dependency job")
        dependency_jobs = [
            scheduled_job
            for scheduled_job in self.jobs
            if scheduled_job.depends_on == event.job_id
        ]
        if dependency_jobs:
            for dependency_job in dependency_jobs:
                logger.debug(f"Dependency job {dependency_job.name} triggered")
                dependency_job.schedule(self.scheduler)

    def save_job_returned_value(self, event):
        """
        Save the return value of a job.
        """
        # TODO
        # Check why not saving on a job with dependency trigger
        logger.debug("Checking if can save job returned value")
        logger.debug(f"Job id {event.job_id}")

        scheduled_job = [
            scheduled_job
            for scheduled_job in self.jobs
            if scheduled_job.name == event.job_id
        ]

        if scheduled_job:
            scheduled_job = scheduled_job[0]
            logger.debug(f"Job to save returned value {scheduled_job.name}")
            return_value = event.retval
            logger.debug(f"Return type {type(return_value)}")
            if isinstance(return_value, pd.DataFrame):
                logger.debug(f"Saving {scheduled_job.name}, return value")
                self.scheduler.add_job(
                    func=scheduled_job.save_execution,
                    kwargs=dict(dataframe=return_value),
                )
            else:
                logger.debug("Return value not a DataFrame")

    def on_job_error(self, event) -> None:
        if event.exception:
            logger.warning(
                f"Job: {event.job_id}, did not run: {event.exception}"
            )

    def on_job_finished(self, event) -> None:
        # TODO
        # Save job events on database
        logger.info(f"Job: {event.job_id}, successfully executed")
        self.trigger_job_dependency(event)
        self.save_job_returned_value(event)

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
        self.scheduler.add_listener(self.on_job_finished, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self.on_job_error, EVENT_JOB_ERROR)

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
