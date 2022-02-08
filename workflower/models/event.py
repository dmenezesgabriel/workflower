import logging
import time

from sqlalchemy import Column, String
from workflower.models.base import BaseModel
from workflower.models.job import Job

logger = logging.getLogger("workflower.models.event")


def _update_job(event, scheduler):
    Job.update_next_run_time(event.job_id, scheduler)
    logger.debug("Checking if need to trigger a dependency job")
    Job.trigger_dependencies(
        event.job_id, scheduler, job_return_value=event.retval
    )


class Event(BaseModel):
    __tablename__ = "events"
    name = Column(
        "name",
        String,
    )
    model = Column(
        "model",
        String,
    )
    model_id = Column(
        "model_id",
        String,
    )
    exception = Column(
        "exception",
        String,
    )
    output = Column(
        "output",
        String,
    )

    def __repr__(self) -> str:
        return (
            f"Event(name={self.name}, "
            f"model={self.model}, "
            f"model_id={self.model_id})"
        )

    @classmethod
    def job_added(cls, event):
        """
        On job added.
        """
        job = Job.get_one(id=event.job_id)
        cls.create(name="job_added", model="job", model_id=job.id)

    @classmethod
    def job_removed(cls, event):
        """
        On job removed.
        """
        job = Job.get_one(id=event.job_id)
        cls.create(name="job_removed", model="job", model_id=job.id)

    @classmethod
    def job_error(cls, event) -> None:
        """
        On job error.
        """
        job = Job.get_one(id=event.job_id)
        cls.create(
            name="job_error",
            model="job",
            model_id=job.id,
            exception=event.exception,
        )

    @classmethod
    def job_executed(cls, event, scheduler) -> None:
        """
        On job executed.
        """
        logger.info(f"Job: {event.job_id}, successfully executed")
        job = Job.get_one(id=event.job_id)
        cls.create(
            name="job_executed",
            model="job",
            model_id=job.id,
            output=event.retval,
        )
        _update_job(event, scheduler)
