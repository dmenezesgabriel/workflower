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
        if self.is_active:
            logger.debug(f"scheduling {self.id}")
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
                self.job = scheduler.add_job(
                    id=str(self.id), **schedule_params
                )
                self.update_next_run_time(self.id, scheduler)
            except ConflictingIdError:
                logger.warning(f"{self.id}, already scheduled, skipping.")
            except ValueError as error:
                # If someone set an invalid date value it will lead
                # to this exception
                logger.error(f"Value error: {error}")
            except Exception as error:
                logger.error(f"Error: {error}")
        else:
            logger.info(f"Job {self.id} is inactive, skipping schedule")

    def unschedule(self, scheduler) -> None:
        logger.debug(f"Unscheduling job: {self.id}")
        try:
            scheduler.remove_job(self.name)
        except JobLookupError:
            logger.warning(
                f"tried to remove {self.name}, " "but it was not scheduled"
            )
