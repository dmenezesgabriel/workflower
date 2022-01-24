"""
Job class.
"""

import logging

import pandas as pd
from apscheduler.jobstores.base import ConflictingIdError
from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from workflower.models.base import BaseModel, database
from workflower.models.workflow import Workflow
from workflower.operators.alteryx import AlteryxOperator
from workflower.operators.papermill import PapermillOperator
from workflower.utils import crud
from workflower.utils.schema import make_job_definition

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
        index=True,
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

    workflow = relationship("Workflow", back_populates="jobs")

    def __init__(self, name, uses, definition, depends_on, workflow):
        self.name = name
        self.uses = uses
        self.definition = definition
        self.depends_on = depends_on
        self.workflow = workflow
        self.job = None

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
                job_definition = make_job_definition(job_dict)
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
    def trigger_dependencies(cls, job_name, scheduler):
        with database.session_scope() as session:
            dependency_jobs = crud.get_all(session, cls, depends_on=job_name)
            if dependency_jobs:
                for dependency_job in dependency_jobs:
                    logger.debug(
                        f"Dependency job {dependency_job.name} triggered"
                    )
                    dependency_job.schedule(scheduler)

    @classmethod
    def save_returned_value(cls, job_name, return_value, scheduler):
        logger.debug(f"Job to save returned value 1 {job_name}")
        with database.session_scope() as session:
            scheduled_job = crud.get_one(session, cls, name=job_name)
            if scheduled_job:
                logger.debug(
                    f"Job to save returned value 2 {scheduled_job.name}"
                )
                logger.debug(f"Return type {type(return_value)}")
                if isinstance(return_value, pd.DataFrame):
                    logger.debug(f"Saving {scheduled_job.name}, return value")
                    scheduler.add_job(
                        func=scheduled_job.save_execution,
                        kwargs=dict(dataframe=return_value),
                    )
                else:
                    logger.debug("Return value not a DataFrame")

    def schedule(self, scheduler) -> None:
        """
        Schedule a job in apscheduler
        """
        job_id = self.definition["id"]
        logger.debug(f"scheduling {job_id}")
        logger.debug(self.definition)
        schedule_args = self.definition.copy()

        if self.uses == "alteryx":
            schedule_args.update(
                dict(func=getattr(AlteryxOperator, "run_workflow"))
            )
        elif self.uses == "papermill":
            schedule_args.update(
                dict(func=getattr(PapermillOperator, "run_notebook"))
            )

        try:
            self.job = scheduler.add_job(**schedule_args)
        except ConflictingIdError:
            logger.warning(f"{job_id}, already scheduled, skipping.")
        except ValueError as error:
            # If someone set an invalid date value it will lead
            # to this exception
            logger.error(f"Value error: {error}")
        except Exception as error:
            logger.error(f"Error: {error}")
