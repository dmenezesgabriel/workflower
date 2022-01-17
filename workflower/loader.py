import logging
import os
from typing import List

import yaml
from config import Config

from workflower.exceptions import InvalidSchemaError, InvalidTypeError
from workflower.job import Job
from workflower.workflow import Workflow

logger = logging.getLogger(__name__)


def validate_schema(configuration_dict: dict) -> bool:
    """
    Validate pipeline file schema
    """
    # TODO
    #  Break in smaller functions
    logger.debug("Validating yml schema")
    #  Pipeline
    pipeline_keys = ["version", "workflow"]
    if not all(key in configuration_dict.keys() for key in pipeline_keys):
        raise InvalidSchemaError(
            "The pipeline must have all of it's keys: "
            f"{', '.join(pipeline_keys)}"
        )
    if not isinstance(configuration_dict["version"], str):
        raise InvalidTypeError("Version must be type string")
    #  Workflow
    if not isinstance(configuration_dict["workflow"], dict):
        raise InvalidTypeError("Workflow wrong definition")
    workflow_keys = ["name", "jobs"]
    workflow = configuration_dict["workflow"]
    if not all(key in workflow.keys() for key in workflow_keys):
        raise InvalidSchemaError(
            "The workflow must have all of it's keys: "
            f"{', '.join(workflow_keys)}"
        )
    if not isinstance(workflow["name"], str):
        raise InvalidTypeError("Name must be type string")
    # Jobs

    workflow_jobs = workflow["jobs"]
    if not isinstance(workflow_jobs, list):
        raise InvalidTypeError("Workflow jobs wrong definition")
    job_keys = ["name", "uses", "trigger"]
    job_trigger_options = ["date", "cron", "interval"]
    job_uses_options = ["alteryx", "papermill"]
    for job in workflow_jobs:
        # Job keys
        if not all(key in job.keys() for key in job_keys):
            raise InvalidSchemaError(
                "The job must have all of it's keys: " f"{', '.join(job_keys)}"
            )
        if not isinstance(job["name"], str):
            raise InvalidTypeError("Name must be type string")
        #  Job uses
        if not isinstance(job["uses"], str):
            raise InvalidTypeError("Name must be type string")
        if job["uses"] not in job_uses_options:
            raise InvalidTypeError(
                f"Job trigger must be: {', '.join(job_uses_options)}"
            )
        if job["uses"] == "papermill":
            papermill_keys = ["input_path", "output_path"]
            if not all(key in job.keys() for key in papermill_keys):
                raise InvalidSchemaError(
                    "Papermill jobs must contain: "
                    f"{', '.join(papermill_keys)}"
                )
        if job["uses"] == "alteryx":
            alteryx_keys = ["path"]
            if not all(key in job.keys() for key in alteryx_keys):
                raise InvalidSchemaError(
                    "Alteryx jobs must contain: " f"{', '.join(alteryx_keys)}"
                )
        # Job triggers
        if not isinstance(job["trigger"], str):
            raise InvalidTypeError("Name must be type string")
        if job["trigger"] not in job_trigger_options:
            raise InvalidTypeError(
                f"Job trigger must be: {', '.join(job_trigger_options)}"
            )
        # TODO
        if job["trigger"] == "date":
            pass
        if job["trigger"] == "cron":
            pass
        if job["trigger"] == "interval":
            pass
    return True


def load_one(workflow_yaml_config_path: str) -> Workflow:
    """
    Load one workflow from a yaml file.
    """
    logger.info(f"Loading pipeline file: {workflow_yaml_config_path}")
    with open(workflow_yaml_config_path) as yf:
        configuration_dict = yaml.safe_load(yf)
    validate_schema(configuration_dict)
    workflow_name = configuration_dict["workflow"]["name"]
    logger.info(f"Workflow found: {workflow_name}")
    #  Preparing jobs
    jobs = []
    workflow_jobs = configuration_dict["workflow"]["jobs"]
    for workflow_job in workflow_jobs:
        job_name = workflow_job["name"]
        new_job_name = workflow_name + "_" + job_name
        workflow_job.update({"name": new_job_name})
        job = Job(name=new_job_name, config=workflow_job)
        jobs.append(job)
    #  Creating workflow object
    workflow = Workflow(name=workflow_name, jobs=jobs)
    return workflow


def load_all(workflows_path: str = Config.WORKFLOWS_FILES_PATH) -> List:
    """
    Load all
    """
    workflows = []
    for root, dirs, files in os.walk(workflows_path):
        for file in files:
            if file.endswith(".yml"):
                workflow_yaml_config_path = os.path.join(root, file)
                try:
                    workflow = load_one(workflow_yaml_config_path)
                    workflows.append(workflow)
                except Exception as error:
                    logger.error(error)
    return workflows
