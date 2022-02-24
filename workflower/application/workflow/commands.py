import logging
from typing import List

from sqlalchemy.exc import IntegrityError
from workflower.application.interfaces.unit_of_work import UnitOfWork
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow
from workflower.schema.parser import WorkflowSchemaParser
from workflower.schema.validator import validate_schema
from workflower.utils.file import (
    get_file_modification_date,
    get_file_name,
    yaml_file_to_dict,
)

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


class LoadWorkflowFromYamlFileCommand:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def execute(self, file_path):
        workflow_parser = WorkflowSchemaParser()
        configuration_dict = yaml_file_to_dict(file_path)
        workflow_name, jobs_dict = workflow_parser.parse_schema(
            configuration_dict
        )
        workflow_file_name = get_file_name(file_path)
        logger.debug(f"Workflow file name: {workflow_file_name}")
        # File name must match with workflow name to workflow be loaded
        if workflow_name != workflow_file_name:
            logger.warning(
                f"Workflow name from {workflow_name}"
                f"don't match with file name {file_path}, "
                "skipping load"
            )
            return
        validate_schema(configuration_dict)
        with self.unit_of_work as uow:
            workflow = uow.workflows.get(name=workflow_name)
            if not workflow:
                workflow = Workflow(
                    name=workflow_name,
                    file_path=file_path,
                )
        return workflow
