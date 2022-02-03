"""
Job class.
"""

import logging

from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from workflower.models.base import BaseModel, database
from workflower.models.workflow import Workflow
from workflower.operators.alteryx import AlteryxOperator
from workflower.operators.papermill import PapermillOperator
from workflower.operators.python import PythonOperator
from workflower.utils import crud
from workflower.utils.schema import JobSchemaParser

logger = logging.getLogger("workflower.job")


class Job(BaseModel):
    __tablename__ = "jobs"
    name = Column(
        "name",
        String,
        unique=True,
        index=True,
    )
    uses = Column(
        "uses",
        String,
    )
    definition = Column(
        "definition",
        JSON,
    )
    depends_on = Column(
        "depends_on",
        String,
    )
    workflow_id = Column(
        "workflow_id",
        Integer,
        ForeignKey("workflows.id"),
    )
    is_active = Column(
        "is_active",
        Boolean,
        default=True,
    )
    next_run_time = Column(
        "next_run_time",
        String,
    )

    workflow = relationship("Workflow", back_populates="jobs")

    def __init__(
        self,
        name,
        uses,
        definition,
        depends_on,
        workflow,
        is_active=True,
        next_run_time=None,
    ):
        self.name = name
        self.uses = uses
        self.definition = definition
        self.depends_on = depends_on
        self.workflow = workflow
        self.is_active = is_active
        self.next_run_time = next_run_time
        self.job = None

    def __repr__(self) -> str:
        return (
            f"Job(name={self.name}, uses={self.uses}, "
            f"definition={self.definition}, "
            f"depends_on={self.depends_on}, "
            f"workflow={self.workflow}, "
            f"next_run_time={self.next_run_time}, "
        )

    @classmethod
    def from_dict(cls, job_dict: dict, workflow_name: str) -> None:
        """
        Job from dict.
        """
        with database.session_scope() as session:
            # Get parent workflow
            workflow = crud.get_one(session, Workflow, name=workflow_name)
            if workflow:
                # Get job attributes from dict
                job_name = job_dict["name"]
                logger.debug(f"Job name: {job_name}")
                # ---
                job_uses = job_dict["uses"]
                logger.debug(f"Job uses: {job_uses}")
                # job_depends_on must point to another job of same workflow
                # Then the event listener will trigger the job by it's id
                job_depends_on = job_dict.get("depends_on", None)
                if job_depends_on:
                    job_depends_on = workflow.name + "_" + job_depends_on
                logger.debug(f"Job depends on: {job_depends_on}")
                # Make apscheduler job definition
                parser = JobSchemaParser()
                job_definition = parser.parse_schema(job_dict)
                # Job name must be unique
                unique_job_id = workflow.name + "_" + job_name
                job_definition.update({"id": unique_job_id})

                # Adding job's relevant information
                crud.get_or_create(
                    session,
                    cls,
                    name=unique_job_id,
                    uses=job_uses,
                    definition=job_definition,
                    depends_on=job_depends_on,
                    workflow=workflow,
                )

                filter_dict = dict(
                    name=unique_job_id,
                )
                update_dict = dict(
                    uses=job_uses,
                    definition=job_definition,
                    depends_on=job_depends_on,
                )
                should_update = False
                if workflow.modified_since_last_load:
                    should_update = True
                if should_update:
                    crud.update(session, cls, filter_dict, update_dict)

    @classmethod
    def deactivate_removed_jobs(cls, configuration_dict: dict) -> None:
        logger.debug("Searching for workflow removed jobs")
        workflow_name = configuration_dict["workflow"]["name"]
        with database.session_scope() as session:
            workflow = crud.get_one(session, Workflow, name=workflow_name)
            if workflow:
                jobs_names = [
                    workflow_name + "_" + job["name"]
                    for job in configuration_dict["workflow"]["jobs"]
                ]
                for job in workflow.jobs:
                    if job.name not in jobs_names:
                        logger.debug(f"Deactivate {job.name}")
                        crud.update(
                            session,
                            cls,
                            {"name": job.name},
                            {"is_active": False},
                        )

    @classmethod
    def unschedule_deactivated_jobs(cls, scheduler) -> None:
        with database.session_scope() as session:
            jobs = crud.get_all(session, cls)
            for job in jobs:
                if not job.is_active:
                    job.unschedule(scheduler)

    @classmethod
    def trigger_dependencies(cls, job_name, scheduler, **kwargs):
        with database.session_scope() as session:
            dependency_jobs = crud.get_all(session, cls, depends_on=job_name)
            if dependency_jobs:
                for dependency_job in dependency_jobs:
                    logger.debug(
                        f"Dependency job {dependency_job.name} triggered"
                    )
                    dependency_job.schedule(scheduler, **kwargs)

    @classmethod
    def update_next_run_time(cls, name, scheduler):
        logger.debug(f"updating next run time for {name}")
        job = scheduler.get_job(name)
        if job:
            logger.debug(f"found job id: {job}")
            cls.update(
                {"name": name},
                {"next_run_time": str(job.next_run_time)},
            )

    def schedule(self, scheduler, **kwargs) -> None:
        """
        Schedule a job in apscheduler
        """
        if self.is_active:
            job_id = self.definition["id"]
            logger.debug(f"scheduling {job_id}")
            logger.debug(self.definition)
            schedule_params = self.definition.copy()
            schedule_kwargs = schedule_params.get("kwargs")
            if schedule_kwargs:
                schedule_kwargs.update(kwargs)

            if self.uses == "alteryx":
                operator = AlteryxOperator
            elif self.uses == "papermill":
                operator = PapermillOperator
            elif self.uses == "python":
                operator = PythonOperator
            schedule_params.update(dict(func=getattr(operator, "execute")))

            try:
                self.job = scheduler.add_job(**schedule_params)
                self.update_next_run_time(self.name, scheduler)
            except ConflictingIdError:
                logger.warning(f"{job_id}, already scheduled, skipping.")
            except ValueError as error:
                # If someone set an invalid date value it will lead
                # to this exception
                logger.error(f"Value error: {error}")
            except Exception as error:
                logger.error(f"Error: {error}")
        else:
            logger.info(f"Job {self.name} is inactive, skipping schedule")

    def unschedule(self, scheduler) -> None:
        logger.debug(f"Unscheduling job: {self.name}")
        try:
            scheduler.remove_job(self.name)
        except JobLookupError:
            logger.warning(
                f"tried to remove {self.name}, " "but it was not scheduled"
            )
