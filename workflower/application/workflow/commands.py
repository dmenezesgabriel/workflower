import logging
from typing import List

from sqlalchemy.exc import IntegrityError
from workflower.application.interfaces.unit_of_work import UnitOfWork
from workflower.domain.entities.workflow import Workflow
from workflower.models.job import Job

logger = logging.getLogger("workflower.application.workflow.commands")


class CreateWorkflowCommand:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def execute(
        self,
        name: str,
        is_active: bool = True,
        file_path: str = None,
        file_exists: bool = None,
        file_last_modified_at: str = None,
        modified_since_last_load: bool = False,
        jobs: List[Job] = None,
    ):
        try:
            with self.unit_of_work as uow:
                workflow = Workflow(
                    name,
                    is_active,
                    file_path,
                    file_exists,
                    file_last_modified_at,
                    modified_since_last_load,
                    jobs,
                )
                uow.workflows.add(workflow)
                return workflow
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")


class AddWorkflowJobCommand:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def execute(self, workflow_id, job_id):
        try:
            with self.unit_of_work as uow:
                workflow = uow.workflows.get(id=workflow_id)
                job = uow.jobs.get(id=job_id)
                workflow.add_job(job)
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
