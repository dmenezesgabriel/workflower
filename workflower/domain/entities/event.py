import logging

from workflower.controllers.job import JobController
from workflower.models.job import Job
from workflower.utils import crud

logger = logging.getLogger("workflower.models.event")


def _update_job(session, event, scheduler):
    Job.update_next_run_time(session, event.job_id, scheduler)
    logger.debug("Checking if need to trigger a dependency job")
    JobController.trigger_dependencies(
        session, event.job_id, scheduler, job_return_value=event.retval
    )


class Event:
    """
    Domain object for events.
    """

    def __init__(self, name, model, model_id, exception, output):
        self.name = name
        self.model = model
        self.model_id = model_id
        self.exception = exception
        self.output = output

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
