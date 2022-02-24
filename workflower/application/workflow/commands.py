import logging
from typing import List

from sqlalchemy.exc import IntegrityError
from workflower.application.interfaces.unit_of_work import UnitOfWork
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow
from workflower.utils.file import get_file_modification_date

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

                if not workflow:
                    logger.info("No matching workflow found")

                elif not job:
                    logger.info("No matching job found")

                elif workflow.has_job(job):
                    logger.info(f"{workflow} already has {job}")

                else:
                    workflow.add_job(job)

        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")


class UpdateModifiedWorkflowFileStateCommand:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def execute(self, workflow_id):
        try:
            with self.unit_of_work as uow:
                workflow = uow.workflows.get(id=workflow_id)

                if not workflow:
                    logger.info("No matching workflow found")
                elif not workflow.file_path:
                    logger.info("No workflow file")

                else:
                    workflow_last_modified_at = str(
                        get_file_modification_date(workflow.file_path)
                    )

                    if (
                        workflow.file_last_modified_at is not None
                        and workflow_last_modified_at
                        != workflow.file_last_modified_at
                    ):
                        workflow.modified_since_last_load = True
                    else:
                        workflow.modified_since_last_load = False

                    workflow.file_last_modified_at = workflow_last_modified_at

        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
