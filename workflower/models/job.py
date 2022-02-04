"""
Job class.
"""

import logging

from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from workflower.models.base import BaseModel, database
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
    workflow = relationship(
        "Workflow",
        back_populates="jobs",
    )
    __table_args__ = (
        UniqueConstraint("name", "workflow_id", name="_name_workflow_id_uc"),
        Index("name_workflow_id_idx", "name", "workflow_id"),
    )

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
    def from_dict(cls, session, job_dict, workflow):
        """
        Create job from dict.
        """
        logger.debug(f"Loading workflow's {workflow} job from dict")
        job_parser = JobSchemaParser()
        (
            job_name,
            job_uses,
            job_depends_on,
            job_definition,
        ) = job_parser.parse_schema(job_dict)
        logger.info(f"Loading job {job_name} of workflow {workflow} from dict")
        # job_depends_on must point to another job of same workflow
        # Then the event listener will trigger the job by it's id
        if job_depends_on:
            logger.debug(f"Job {job_name} has dependency")
            dependency_job = crud.get_one(
                session,
                cls,
                workflow_id=workflow.id,
                name=job_depends_on,
            )
            job_depends_on_id = dependency_job.id
            logger.debug(f"Job {job_name} depends on: {job_depends_on_id}")
        else:
            logger.debug(f"Job {job_name} has no dependency")
            job_depends_on_id = None

        # Adding job's relevant information
        logger.debug(f"Checking if job {job_name} exists")
        job = crud.get_one(
            session, cls, name=job_name, workflow_id=workflow.id
        )
        if job:
            logger.debug(f"Checking if job {job_name} found: {job}")
            if workflow.modified_since_last_load:
                logger.debug(f"Workflow {workflow.id} has been modified")
                filter_dict = dict(
                    id=job.id,
                )
                update_dict = dict(
                    uses=job_uses,
                    definition=job_definition,
                    depends_on=job_depends_on_id,
                    is_active=True,
                )
                logger.debug(f"Updating {job}")
                crud.update(session, cls, filter_dict, update_dict)
        elif not job:
            logger.debug(f"Creating job :{job_name}")
            job = crud.create(
                session,
                cls,
                name=job_name,
                uses=job_uses,
                definition=job_definition,
                depends_on=job_depends_on_id,
                workflow=workflow,
            )

    @classmethod
    def trigger_dependencies(cls, job_id, scheduler, **kwargs):
        """
        Trigger job's dependencies.
        """
        with database.session_scope() as session:
            dependency_jobs = crud.get_all(session, cls, depends_on=job_id)
            if dependency_jobs:
                for dependency_job in dependency_jobs:
                    logger.debug(
                        f"Dependency job {dependency_job.name} triggered"
                    )
                    dependency_job.schedule(scheduler, **kwargs)

    @classmethod
    def update_next_run_time(cls, id, scheduler):
        """
        Update next_run_time in database's object row.
        """
        logger.debug(f"updating next run time for {id}")
        job = scheduler.get_job(id)
        if job:
            logger.debug(f"found job id: {job}")
            cls.update(
                {"id": id},
                {"next_run_time": str(job.next_run_time)},
            )

    def schedule(self, scheduler, **kwargs) -> None:
        """
        Schedule a job in apscheduler
        """
        logger.info(f"scheduling job: {self}")
        schedule_params = self.definition.copy()
        schedule_kwargs = schedule_params.get("kwargs")
        if schedule_kwargs:
            schedule_kwargs.update(kwargs)

        if self.uses == "alteryx":
            logger.debug("Job uses Alteryx")
            operator = AlteryxOperator
        elif self.uses == "papermill":
            logger.debug("Job uses Papermill")
            operator = PapermillOperator
        elif self.uses == "python":
            logger.debug("Job uses Python")
            operator = PythonOperator
        schedule_params.update(dict(func=getattr(operator, "execute")))

        try:
            self.job = scheduler.add_job(id=str(self.id), **schedule_params)
            self.update_next_run_time(self.id, scheduler)
            logger.debug(f"Job {self} successfully scheduled")
        except ConflictingIdError:
            logger.warning(f"{self}, already scheduled, skipping.")
        except ValueError as error:
            # If someone set an invalid date value it will lead
            # to this exception
            logger.error(f"{self} value error: {error}")
        except Exception as error:
            logger.error(f"Error: {error}")

    def unschedule(self, scheduler) -> None:
        """
        Unschedule job
        """
        logger.debug(f"Unscheduling job: {self}")
        try:
            scheduler.remove_job(self.id)
        except JobLookupError:
            logger.warning(
                f"tried to remove {self}, " "but it was not scheduled"
            )
