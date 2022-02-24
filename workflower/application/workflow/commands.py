import logging
from typing import List

from sqlalchemy.exc import IntegrityError
from workflower.application.interfaces.unit_of_work import UnitOfWork
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow
from workflower.schema.parser import JobSchemaParser, WorkflowSchemaParser
from workflower.schema.validator import validate_schema
from workflower.utils.file import (
    get_file_modification_date,
    get_file_name,
    yaml_file_to_dict,
)

logger = logging.getLogger("workflower.application.workflow.commands")


class CreateWorkflowCommand:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        name: str,
        is_active: bool = True,
        file_path: str = None,
        file_exists: bool = None,
        file_last_modified_at: str = None,
        modified_since_last_load: bool = False,
        jobs: List[Job] = None,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.name = name
        self.is_active = is_active
        self.file_path = file_path
        self.file_exists = file_exists
        self.file_last_modified_at = file_last_modified_at
        self.modified_since_last_load = modified_since_last_load
        self.jobs = jobs

    def execute(self):
        try:
            with self.unit_of_work as uow:
                workflow = Workflow(
                    self.name,
                    self.is_active,
                    self.file_path,
                    self.file_exists,
                    self.file_last_modified_at,
                    self.modified_since_last_load,
                    self.jobs,
                )
                uow.workflows.add(workflow)
                return workflow
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")


class AddWorkflowJobCommand:
    def __init__(self, unit_of_work: UnitOfWork, workflow_id, job_id) -> None:
        self.unit_of_work = unit_of_work
        self.workflow_id = workflow_id
        self.job_id = job_id

    def execute(self):
        try:
            with self.unit_of_work as uow:
                workflow = uow.workflows.get(id=self.workflow_id)
                job = uow.jobs.get(id=self.job_id)

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
    def __init__(self, unit_of_work: UnitOfWork, workflow_id) -> None:
        self.unit_of_work = unit_of_work
        self.workflow_id = workflow_id

    def execute(self):
        try:
            with self.unit_of_work as uow:
                workflow = uow.workflows.get(id=self.workflow_id)

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
    def __init__(self, unit_of_work: UnitOfWork, file_path) -> None:
        self.unit_of_work = unit_of_work
        self.file_path = file_path

    def execute(self):
        workflow_parser = WorkflowSchemaParser()
        configuration_dict = yaml_file_to_dict(self.file_path)
        workflow_name, jobs_dict = workflow_parser.parse_schema(
            configuration_dict
        )
        workflow_file_name = get_file_name(self.file_path)
        logger.debug(f"Workflow file name: {workflow_file_name}")
        # File name must match with workflow name to workflow be loaded
        if workflow_name != workflow_file_name:
            logger.warning(
                f"Workflow name from {workflow_name}"
                f"don't match with file name {self.file_path}, "
                "skipping load"
            )
            return
        validate_schema(configuration_dict)
        with self.unit_of_work as uow:
            workflow = uow.workflows.get(name=workflow_name)
            if not workflow:
                workflow = Workflow(
                    name=workflow_name,
                    file_path=self.file_path,
                )
                uow.workflows.add(workflow)
            # Add jobs
            jobs_list = []
            for job_dict in jobs_dict:
                job_parser = JobSchemaParser()
                (
                    job_name,
                    job_operator,
                    job_depends_on,
                    dependency_logs_pattern,
                    run_if_pattern_match,
                    job_definition,
                ) = job_parser.parse_schema(job_dict)
                if job_depends_on:
                    dependency_job = uow.jobs.get(
                        name=job_depends_on, workflow_id=workflow.id
                    )
                    job_depends_on_id = dependency_job.id
                else:
                    job_depends_on_id = None
                # Check if job already exists
                job = uow.jobs.get(name=job_name, workflow_id=workflow.id)
                if job:
                    if workflow.modified_since_last_load:
                        job.operator = job_operator
                        job.definition = job_definition
                        job.depends_on = job_depends_on_id
                        job.dependency_logs_pattern = dependency_logs_pattern
                        job.run_if_pattern_match = run_if_pattern_match
                        job.is_active = True
                elif not job:
                    job = Job(
                        name=job_name,
                        operator=job_operator,
                        definition=job_definition,
                        depends_on=job_depends_on_id,
                        dependency_logs_pattern=dependency_logs_pattern,
                        run_if_pattern_match=run_if_pattern_match,
                    )

                if workflow.has_job(job):
                    continue
                else:
                    workflow.add_job(job)
                jobs_list.append(job)
                for old_job in workflow.jobs:
                    if old_job not in jobs_list:
                        workflow.remove_job(old_job)
        return workflow


class DeactivateWorkflowJobsCommand:
    def __init__(self, unit_of_work: UnitOfWork, workflow_id) -> None:
        self.unit_of_work = unit_of_work
        self.workflow_id = workflow_id

    def execute(self):
        try:
            with self.unit_of_work as uow:
                workflow = uow.workflows.get(id=self.workflow_id)

                if not workflow:
                    logger.info("No matching workflow found")
                elif not workflow.file_path:
                    logger.info("No workflow file")

                else:
                    if workflow.jobs:
                        for job in workflow.jobs:
                            job.is_active = False

        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")


class ActivateWorkflowJobsCommand:
    def __init__(self, unit_of_work: UnitOfWork, workflow_id) -> None:
        self.unit_of_work = unit_of_work
        self.workflow_id = workflow_id

    def execute(self):
        try:
            with self.unit_of_work as uow:
                workflow = uow.workflows.get(id=self.workflow_id)

                if not workflow:
                    logger.info("No matching workflow found")
                elif not workflow.file_path:
                    logger.info("No workflow file")

                else:
                    if workflow.jobs:
                        for job in workflow.jobs:
                            job.is_active = True

        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
