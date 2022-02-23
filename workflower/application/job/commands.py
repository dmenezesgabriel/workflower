import logging

from sqlalchemy.exc import IntegrityError
from workflower.application.interfaces.unit_of_work import UnitOfWork
from workflower.domain.entities.job import Job

logger = logging.getLogger("workflower.application.job.commands")


class CreateJobCommand:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def execute(
        self,
        name: str,
        operator: str,
        definition: dict,
        workflow=None,
        depends_on: str = None,
        dependency_logs_pattern: str = None,
        run_if_pattern_match: bool = True,
        is_active: bool = True,
        next_run_time: bool = None,
    ):
        try:
            with self.unit_of_work as uow:
                job = Job(
                    name,
                    operator,
                    definition,
                    workflow,
                    depends_on,
                    dependency_logs_pattern,
                    run_if_pattern_match,
                    is_active,
                    next_run_time,
                )
                uow.jobs.add(job)
                return job
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
