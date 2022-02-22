"""
Workflow class.
import os
"""
import logging

from workflower.models.job import Job
from workflower.schema.parser import WorkflowSchemaParser
from workflower.schema.validator import validate_schema
from workflower.utils import crud
from workflower.utils.file import (
    get_file_modification_date,
    get_file_name,
    yaml_file_to_dict,
)

logger = logging.getLogger("workflower.models.workflow")


class Workflow:
    """
    Domain object for the workflow.

    Args:
        - name (str): Name of the given workflow.
        - file_path(str, optional): Path of workflow file.
        - file_last_modified_at (int, optional): time since epoch of
        last file modification.
        - is_active (bool, optional): Workflow is active or not.
        - modified_since_last_load (bool, optional): Workflow has been modified
        since las load or not.
        - jobs (List[Job]): List of jobs for the workflow.
    """

    def __init__(
        self,
        name,
        file_path=None,
        file_exists=None,
        file_last_modified_at=None,
        is_active=True,
        modified_since_last_load=False,
        jobs=[],
    ):
        self.name = name
        self.file_path = file_path
        self.file_exists = file_exists
        self.file_last_modified_at = file_last_modified_at
        self.modified_since_last_load = modified_since_last_load
        self.is_active = is_active
        self.jobs = jobs

    def __repr__(self) -> str:
        return (
            f"Workflow(name={self.name}, file_path={self.file_path}, "
            f"file_last_modified_at={self.file_last_modified_at}, "
            f"modified_since_last_load={self.modified_since_last_load}, "
            f"is_active={self.is_active}"
        )

    @classmethod
    def update_modified_file_state(cls, session, workflow, file_path):
        """
        Set or update workflow file modification date.
        """

        workflow_last_modified_at = str(get_file_modification_date(file_path))
        filter_dict = {"id": workflow.id}
        update_dict = {"file_last_modified_at": workflow_last_modified_at}
        if (
            workflow.file_last_modified_at is not None
            and workflow_last_modified_at != workflow.file_last_modified_at
        ):
            update_dict.update({"modified_since_last_load": True})
        else:
            update_dict.update({"modified_since_last_load": False})

        crud.update(session, cls, filter_dict, update_dict)

    @classmethod
    def from_dict(cls, session, configuration_dict, file_path=None):
        """
        Workflow from dict.
        """
        workflow_parser = WorkflowSchemaParser()
        workflow_name, jobs_dict = workflow_parser.parse_schema(
            configuration_dict
        )
        logger.info(f"Workflow found: {workflow_name}")
        if file_path:
            workflow_file_name = get_file_name(file_path)
            logger.debug(f"Workflow file name: {workflow_file_name}")
            # File name must match with workflow name to workflow be loaded
            if workflow_name != workflow_file_name:
                logger.warning(
                    f"Workflow name from {workflow_name}"
                    f"don't match with file name {file_path}, "
                    "skipping load"
                )
                return
        validate_schema(configuration_dict)
        #  Creating workflow object
        workflow = crud.get_one(
            session,
            cls,
            name=workflow_name,
        )
        if workflow:
            if file_path:
                #  Checking file modification date
                cls.update_modified_file_state(session, workflow, file_path)
                crud.update(
                    session,
                    cls,
                    dict(id=workflow.id),
                    dict(is_active=True),
                )
                workflow.update_jobs(session, jobs_dict)
        elif not workflow:
            workflow = crud.create(
                session,
                cls,
                name=workflow_name,
                file_path=file_path,
            )
        logger.debug(f"workflow object: {workflow}")
        logger.debug("Loading or updating jobs")
        for workflow_job_dict in jobs_dict:
            # Get job attributes from dict
            # Make apscheduler job definition
            Job.from_dict(session, workflow_job_dict, workflow)
        return workflow

    @classmethod
    def from_yaml(cls, session, file_path):
        """
        Workflow from yaml file.
        """
        configuration_dict = yaml_file_to_dict(file_path)
        return cls.from_dict(session, configuration_dict, file_path)

    def update_jobs(
        self,
        session,
        jobs_dict,
    ) -> None:
        logger.debug("Searching for workflow removed jobs")
        jobs_names = [job["name"] for job in jobs_dict]
        for job in self.jobs:
            if job.name not in jobs_names:
                logger.debug(f"Deactivate {job.name}")
                crud.update(
                    session,
                    Job,
                    dict(name=job.name),
                    dict(is_active=False, next_run_time=None),
                )
            else:
                crud.update(
                    session,
                    Job,
                    dict(name=job.name),
                    dict(is_active=True),
                )

    def activate_all_jobs(self, session):
        for job in self.jobs:
            logger.debug(f"Activate {job.name}")
            crud.update(
                session,
                Job,
                dict(name=job.name),
                dict(is_active=True),
            )

    def deactivate_all_jobs(self, session):
        for job in self.jobs:
            logger.debug(f"Deactivate {job.name}")
            crud.update(
                session,
                Job,
                dict(name=job.name),
                dict(is_active=False, next_run_time=None),
            )

    def schedule_jobs(self, session, scheduler):
        """
        Schedule workflow's jobs.
        """
        logger.info(f"Scheduling jobs from workflow {self.id}")
        for job in self.jobs:
            # If job has dependencies wait till the event of
            # it's job dependency occurs
            if job.is_active:
                if job.depends_on:
                    logger.info(
                        f"{job.name} depends on {job.depends_on}, "
                        "putting to wait"
                    )
                    continue
                job.schedule(scheduler)
                Job.update_next_run_time(session, job.id, scheduler)

    def unschedule_jobs(self, scheduler):
        """
        Unschedule workflow's jobs.
        """
        for job in self.jobs:
            logger.info(f"Removing {job.name}")
            try:
                job.unschedule(scheduler)
            except Exception as error:
                logger.error(f"Try to remove {job.name} failed: {error}")
