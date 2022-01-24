"""
Workflow class.
import os
"""
import logging
import os

from apscheduler.jobstores.base import JobLookupError
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship
from workflower.models.base import BaseModel, database
from workflower.utils import crud
from workflower.utils.file import get_file_modification_date, get_file_name

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
        String,
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

    @classmethod
    def from_dict(cls, workflow_yaml_config_path, configuration_dict):
        """
        Workflow from dict.
        """
        with database.session_scope() as session:
            workflow_file_name = get_file_name(workflow_yaml_config_path)
            logger.debug(f"Workflow file name: {workflow_file_name}")
            workflow_name = configuration_dict["workflow"]["name"]
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
            workflow = crud.get_or_create(
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
    def schedule_all_jobs(cls, scheduler):
        with database.session_scope() as session:
            workflows = crud.get_all(session, cls)
            for workflow in workflows:
                if workflow.modified_since_last_load:
                    logger.info(
                        f"{workflow.name} file has been modified, "
                        "unscheduling  jobs"
                    )
                    workflow.unschedule_jobs(scheduler)
                if not workflow.file_exists:
                    logger.info(
                        f"{workflow.name} file has been removed, "
                        "unscheduling  jobs"
                    )
                    workflow.unschedule_jobs(scheduler)
                logger.info("Scheduling jobs")
                workflow.schedule_jobs(scheduler)

    def schedule_jobs(self, scheduler):
        for job in self.jobs:
            # If job has dependencies wait till the event of
            # it's job dependency occurs
            if job.depends_on:
                logger.info(
                    f"{job.name} depends on {job.depeds_on}, putting to wait"
                )
                continue
            job.schedule(scheduler)

    def unschedule_jobs(self, scheduler):
        for job in self.jobs:
            logger.info(f"Removing {job.name}")
            try:
                scheduler.remove_job(job.name)
            except JobLookupError:
                logger.warning(
                    f"tried to remove {job.name}, " "but it was not scheduled"
                )
            except Exception as error:
                logger.error(f"Try to remove {job.name} failed: {error}")
