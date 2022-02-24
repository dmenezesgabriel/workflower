import logging

from sqlalchemy.exc import IntegrityError
from workflower.application.interfaces.unit_of_work import UnitOfWork
from workflower.domain.entities.job import Job

logger = logging.getLogger("workflower.application.job.commands")


class CreateJobCommand:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        name: str,
        operator: str,
        definition: dict,
        workflow=None,
        depends_on: str = None,
        dependency_logs_pattern: str = None,
        run_if_pattern_match: bool = True,
        is_active: bool = True,
        next_run_time: bool = None,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.name = name
        self.operator = operator
        self.definition = definition
        self.workflow = workflow
        self.depends_on = depends_on
        self.dependency_logs_pattern = dependency_logs_pattern
        self.run_if_pattern_match = run_if_pattern_match
        self.run_if_pattern_match = run_if_pattern_match
        self.is_active = is_active
        self.next_run_time = next_run_time

    def execute(self):
        try:
            with self.unit_of_work as uow:
                job = Job(
                    self.name,
                    self.operator,
                    self.definition,
                    self.workflow,
                    self.depends_on,
                    self.dependency_logs_pattern,
                    self.run_if_pattern_match,
                    self.is_active,
                    self.next_run_time,
                )
                uow.jobs.add(job)
                return job
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
