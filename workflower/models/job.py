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
from workflower.models.base import BaseModel
from workflower.operators.factory import create_operator
from workflower.plugins.factory import create_plugin
from workflower.schema.parser import JobSchemaParser
from workflower.utils import crud

logger = logging.getLogger("workflower.job")


class Job(BaseModel):
    __tablename__ = "jobs"
    name = Column(
        "name",
        String,
    )
    operator = Column(
        "operator",
        String,
    )
    definition = Column(
        "definition",
        JSON,
    )
    # TODO
    # depends on trigger should be a apscheduler.abc.Trigger subclass.
    # This code is too coupled :(
    # Another option is consume this from definition to be less coupled.
    # =========================================================================
    depends_on = Column(
        "depends_on",
        String,
    )
    dependency_logs_pattern = Column(
        "dependency_logs_pattern",
        String,
    )
    run_if_pattern_match = Column(
        "run_if_pattern_match",
        Boolean,
        default=True,
    )
    # =========================================================================
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
        operator,
        definition,
        depends_on,
        workflow,
        dependency_logs_pattern=None,
        run_if_pattern_match=True,
        is_active=True,
        next_run_time=None,
    ):
        # TODO
        # Add state according with triggers
        # scheduled
        # running
        # executed (if trigger says tha should run only once)
        self.name = name
        self.operator = operator
        self.definition = definition
        self.depends_on = depends_on
        self.dependency_logs_pattern = dependency_logs_pattern
        self.run_if_pattern_match = run_if_pattern_match
        self.workflow = workflow
        self.is_active = is_active
        self.next_run_time = next_run_time
        self.job_scheduled_ref = None

    def __repr__(self) -> str:
        return (
            f"Job(name={self.name}, operator={self.operator}, "
            f"definition={self.definition}, "
            f"depends_on={self.depends_on}, "
            f"dependency_logs_pattern={self.dependency_logs_pattern}, "
            f"run_if_pattern_match={self.run_if_pattern_match}, "
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
            job_operator,
            job_depends_on,
            dependency_logs_pattern,
            run_if_pattern_match,
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
                    operator=job_operator,
                    definition=job_definition,
                    depends_on=job_depends_on_id,
                    dependency_logs_pattern=dependency_logs_pattern,
                    run_if_pattern_match=run_if_pattern_match,
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
                operator=job_operator,
                definition=job_definition,
                depends_on=job_depends_on_id,
                dependency_logs_pattern=dependency_logs_pattern,
                run_if_pattern_match=run_if_pattern_match,
                workflow=workflow,
            )

    @classmethod
    def update_next_run_time(cls, session, id, scheduler):
        """
        Update next_run_time in database's object row.
        """
        logger.debug(f"updating next run time for {id}")
        job = scheduler.get_job(id)
        if job:
            logger.debug(f"found job id: {job}")
            crud.update(
                session,
                cls,
                dict(id=id),
                dict(next_run_time=str(job.next_run_time)),
            )

    def build_schedule_params(self, **kwargs):
        """
        Build schedule params.
        """
        schedule_params = self.definition.copy()
        schedule_kwargs = schedule_params.get("kwargs")
        plugins = schedule_kwargs.get("plugins")
        if plugins:
            plugins_list = list(
                map(lambda plugin_name: create_plugin(plugin_name), plugins)
            )
            schedule_kwargs.update(dict(plugins=plugins_list))
        if schedule_kwargs:
            schedule_kwargs.update(kwargs)

        operator = create_operator(self.operator)
        schedule_params.update(dict(func=getattr(operator, "execute")))
        return schedule_params

    def schedule(self, scheduler, **kwargs):
        """
        Schedule a job in apscheduler
        """
        logger.info(f"scheduling job: {self}")
        schedule_params = self.build_schedule_params(**kwargs)

        try:
            self.job_scheduled_ref = scheduler.add_job(
                id=str(self.id), **schedule_params
            )
            logger.debug(f"Job {self} successfully scheduled")
            return self.job_scheduled_ref
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
