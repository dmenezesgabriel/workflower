import logging
import os
from typing import List

import yaml
from config import Config

from workflower.models.job import JobWrapper
from workflower.models.workflow import WorkflowWrapper
from workflower.utils.schema import make_job_definition, validate_schema

logger = logging.getLogger("workflower.loader")


def get_file_modification_date(file_path):
    return os.path.getmtime(file_path)


def load_one(workflow_yaml_config_path: str) -> WorkflowWrapper:
    """
    Load one workflow from a yaml file.
    """
    # TODO
    # Pytest this function
    logger.info(f"Loading pipeline file: {workflow_yaml_config_path}")
    with open(workflow_yaml_config_path) as yf:
        configuration_dict = yaml.safe_load(yf)
    # Validate file
    validate_schema(configuration_dict)
    # File name must match with workflow name to workflow be loaded
    workflow_file_name = os.path.splitext(
        os.path.basename(workflow_yaml_config_path)
    )[0]
    logger.debug(f"Workflow file name: {workflow_file_name}")
    workflow_name = configuration_dict["workflow"]["name"]
    logger.info(f"Workflow found: {workflow_name}")
    if workflow_name != workflow_file_name:
        logger.warning(
            f"Workflow name from {workflow_name}"
            f"don't match with file name {workflow_yaml_config_path}, "
            "skipping load"
        )
        return
    # Preparing jobs
    jobs = []
    # TODO
    # Wrap workflow name + job name operations on a separated function
    workflow_jobs = configuration_dict["workflow"]["jobs"]
    for workflow_job in workflow_jobs:
        job_name = workflow_job["name"]
        logger.debug(f"Job name: {job_name}")
        job_uses = workflow_job["uses"]
        logger.debug(f"Job uses: {job_uses}")
        # job_depends_on must point to another job of same workflow
        # Then the event listener will trigger the job by it's id
        job_depends_on = workflow_job.get("depends_on", None)
        if job_depends_on:
            job_depends_on = workflow_name + "_" + job_depends_on
        logger.debug(f"Job depends on: {job_depends_on}")
        # Make apscheduler job definition
        job_definition = make_job_definition(workflow_job)
        # Job name must be unique
        unique_job_id = workflow_name + "_" + job_name
        job_definition.update({"id": unique_job_id})
        # Adding job's relevant information
        job = JobWrapper(
            name=unique_job_id,
            uses=job_uses,
            definition=job_definition,
            depends_on=job_depends_on,
        )
        jobs.append(job)
    logger.debug(f"Workflow jobs {[job.name for job in jobs]}")
    #  Creating workflow object
    workflow_last_modified_at = os.path.getmtime(workflow_yaml_config_path)
    workflow = WorkflowWrapper(
        name=workflow_name,
        jobs=jobs,
        last_modified_at=workflow_last_modified_at,
    )
    return workflow


def load_all(workflows_path: str = Config.WORKFLOWS_FILES_PATH) -> List:
    """
    Load all.
    """
    # TODO
    # Pytest this function
    workflows = []
    for root, dirs, files in os.walk(workflows_path):
        for file in files:
            if file.endswith(".yml") or file.endswith(".yaml"):
                workflow_yaml_config_path = os.path.join(root, file)
                try:
                    workflow = load_one(workflow_yaml_config_path)
                    if workflow:
                        workflows.append(workflow)
                except Exception as error:
                    logger.error(error)
    return workflows
