"""
Workflow class.
import os
"""
import logging
import os

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship
from workflower.models.base import BaseModel, database
from workflower.models.job import Job
from workflower.utils import crud
from workflower.utils.file import (
    get_file_modification_date,
    get_file_name,
    yaml_file_to_dict,
)
from workflower.utils.schema import (
    JobSchemaParser,
    WorkflowSchemaParser,
    validate_schema,
)

logger = logging.getLogger("workflower.models.workflow")


class Workflow(BaseModel):
    __tablename__ = "workflows"
    name = Column(
        "name",
        String,
        unique=True,
        index=True,
    )
    file_path = Column(
        "file_path",
        String,
        unique=True,
    )
    file_exists = Column(
        "file_exists",
        Boolean,
        default=True,
    )
    is_active = Column(
        "is_active",
        Boolean,
        default=True,
    )
    file_last_modified_at = Column(
        "file_last_modified_at",
        String,
    )
    modified_since_last_load = Column(
        "modified_since_last_load",
        Boolean,
        default=False,
    )
    jobs = relationship("Job")

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
    def from_yaml(cls, workflow_yaml_config_path):
        """
        Workflow from dict.
        """
        configuration_dict = yaml_file_to_dict(workflow_yaml_config_path)
        validate_schema(configuration_dict)
        workflow_parser = WorkflowSchemaParser()
        workflow_name, jobs_dict = workflow_parser.parse_schema(
            configuration_dict
        )
        with database.session_scope() as session:
            workflow_file_name = get_file_name(workflow_yaml_config_path)
            logger.debug(f"Workflow file name: {workflow_file_name}")
            logger.info(f"Workflow found: {workflow_name}")
            # File name must match with workflow name to workflow be loaded
            if workflow_name != workflow_file_name:
                logger.warning(
                    f"Workflow name from {workflow_name}"
                    f"don't match with file name {workflow_yaml_config_path}, "
                    "skipping load"
                )
                return

            #  Creating workflow object
            workflow = crud.get_one(
                session,
                cls,
                name=workflow_name,
            )
            if not workflow:
                workflow = crud.create(
                    session,
                    cls,
                    name=workflow_name,
                    file_path=workflow_yaml_config_path,
                )
            #  Checking file modification date
            cls.set_workflow_modification_date(
                workflow_yaml_config_path, workflow_name
            )
            logger.debug(f"workflow object: {workflow}")
            logger.debug("Loading jobs")
            cls.deactivate_removed_jobs(workflow_name, jobs_dict)
            for workflow_job_dict in jobs_dict:
                # Get job attributes from dict
                # Make apscheduler job definition
                job_parser = JobSchemaParser()
                (
                    job_name,
                    job_uses,
                    job_depends_on,
                    job_definition,
                ) = job_parser.parse_schema(workflow_job_dict)

                # job_depends_on must point to another job of same workflow
                # Then the event listener will trigger the job by it's id
                if job_depends_on:

                    dependency_job = crud.get_one(
                        session,
                        Job,
                        workflow_id=workflow.id,
                        name=job_depends_on,
                    )

                    job_depends_on_id = dependency_job.id
                    logger.debug(f"Job depends on: {job_depends_on_id}")
                else:
                    job_depends_on_id = None

                # Adding job's relevant information

                job = crud.get_one(
                    session, Job, name=job_name, workflow_id=workflow.id
                )
                if not job:
                    job = crud.create(
                        session,
                        Job,
                        name=job_name,
                        uses=job_uses,
                        definition=job_definition,
                        depends_on=job_depends_on_id,
                        workflow=workflow,
                    )

                filter_dict = dict(
                    id=job.id,
                )
                update_dict = dict(
                    uses=job_uses,
                    definition=job_definition,
                    depends_on=job_depends_on_id,
                )
                should_update = False
                if workflow.modified_since_last_load:
                    should_update = True
                if should_update:
                    crud.update(session, Job, filter_dict, update_dict)

    @classmethod
    def set_workflow_modification_date(
        cls, workflow_yaml_config_path, workflow_name
    ):
        """
        Set or update workflow file modification date.
        """
        with database.session_scope() as session:
            workflow = crud.get_one(session, cls, name=workflow_name)
            filter_dict = {"name": workflow_name}
            workflow_last_modified_at = str(
                get_file_modification_date(workflow_yaml_config_path)
            )
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
    def set_files_still_exists(cls):
        with database.session_scope() as session:
            workflows = crud.get_all(session, cls)
            for workflow in workflows:
                file_exists = os.path.isfile(workflow.file_path)
                if file_exists:
                    logger.debug(f"{workflow.name} file exists")
                    update_dict = {"file_exists": True}
                else:
                    logger.info(f"{workflow.name} file not exists")
                    update_dict = {"file_exists": False}
                filter_dict = {"name": workflow.name}
                crud.update(session, cls, filter_dict, update_dict)

    @classmethod
    def deactivate_removed_jobs(cls, workflow_name, jobs_dict) -> None:
        logger.debug("Searching for workflow removed jobs")
        with database.session_scope() as session:
            workflow = crud.get_one(session, cls, name=workflow_name)
            if workflow:
                jobs_names = [job["name"] for job in jobs_dict]
                for job in workflow.jobs:
                    if job.name not in jobs_names:
                        logger.debug(f"Deactivate {job.name}")
                        crud.update(
                            session,
                            Job,
                            {"name": job.name},
                            {
                                "is_active": False,
                                "next_run_time": None,
                            },
                        )

    @classmethod
    def schedule_all_jobs(cls, scheduler):
        with database.session_scope() as session:
            jobs = crud.get_all(session, Job)
            for job in jobs:
                if not job.is_active:
                    job.unschedule(scheduler)
            workflows = crud.get_all(session, cls)
            for workflow in workflows:
                if workflow.modified_since_last_load is True:
                    logger.info(
                        f"{workflow.name} file has been modified, "
                        "unscheduling jobs"
                    )
                    workflow.unschedule_jobs(scheduler)
                if workflow.file_exists is False:
                    logger.info(
                        f"{workflow.name} file has been removed, "
                        "unscheduling jobs"
                    )
                    workflow.unschedule_jobs(scheduler)
                    logger.debug(
                        f"{workflow.name} inactive is inactive, skipping"
                    )
                    cls.update({"id": workflow.id}, {"is_active": False})
                    continue
                logger.info("Scheduling jobs")
                workflow.schedule_jobs(scheduler)

    def schedule_jobs(self, scheduler):
        if self.file_exists:
            for job in self.jobs:
                # If job has dependencies wait till the event of
                # it's job dependency occurs
                if job.depends_on:
                    logger.info(
                        f"{job.name} depends on {job.depends_on}, "
                        "putting to wait"
                    )
                    continue
                job.schedule(scheduler)
        else:
            logger.info(f"{self.name} file removed, skipping")

    def unschedule_jobs(self, scheduler):
        for job in self.jobs:
            logger.info(f"Removing {job.name}")
            try:
                job.unschedule(scheduler)
            except Exception as error:
                logger.error(f"Try to remove {job.name} failed: {error}")
