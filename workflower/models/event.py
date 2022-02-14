import logging

from sqlalchemy import Column, String
from workflower.models.base import BaseModel
from workflower.models.job import Job
from workflower.utils import crud

logger = logging.getLogger("workflower.models.event")


def _update_job(session, event, scheduler):
    Job.update_next_run_time(session, event.job_id, scheduler)
    logger.debug("Checking if need to trigger a dependency job")
    Job.trigger_dependencies(
        session, event.job_id, scheduler, job_return_value=event.retval
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
    def job_added(cls, session, event):
        """
        On job added.
        """
        job = crud.get_one(session, Job, id=event.job_id)
        crud.create(
            session, cls, name="job_added", model="job", model_id=job.id
        )

    @classmethod
    def job_removed(cls, session, event):
        """
        On job removed.
        """
        job = crud.get_one(session, Job, id=event.job_id)
        crud.create(
            session, cls, name="job_removed", model="job", model_id=job.id
        )

    @classmethod
    def job_error(cls, session, event) -> None:
        """
        On job error.
        """
        job = crud.get_one(session, Job, id=event.job_id)
        crud.create(
            session,
            cls,
            name="job_error",
            model="job",
            model_id=job.id,
            exception=event.exception,
        )

    @classmethod
    def job_executed(cls, session, event, scheduler) -> None:
        """
        On job executed.
        """
        logger.info(f"Job: {event.job_id}, successfully executed")
        job = crud.get_one(session, Job, id=event.job_id)
        crud.create(
            session,
            cls,
            name="job_executed",
            model="job",
            model_id=job.id,
            output=event.retval,
        )
        _update_job(session, event, scheduler)
