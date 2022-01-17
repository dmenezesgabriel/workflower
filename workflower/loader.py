import logging
import os
from tkinter import E

import yaml
from config import Config

from workflower.exceptions import InvalidSchemaError, InvalidTypeError
from workflower.job import Job
from workflower.workflow import Workflow

logger = logging.getLogger(__name__)


def validate_schema(configuration_dict):
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
        raise InvalidTypeError(
            "Workflow must contain name and job information"
        )
    workflow_keys = ["name", "jobs"]
    workflow = configuration_dict["workflow"]
    if not all(key in workflow.keys() for key in workflow_keys):
        raise InvalidSchemaError(
            "The workflow must have all of it's keys: "
            f"{', '.join(workflow_keys)}"
        )
    if not isinstance(workflow["name"], str):
        raise InvalidTypeError("Version must be type string")
    # Jobs
    workflow_jobs = workflow["jobs"]
    job_keys = ["name", "uses", "trigger"]
    for job in workflow_jobs:
        if not all(key in job.keys() for key in job_keys):
            raise InvalidSchemaError(
                "The job must have all of it's keys: " f"{', '.join(job_keys)}"
            )
    return True


def load_one(workflow_yaml_config_path):
    logger.debug("Loading pipeline")
    with open(workflow_yaml_config_path) as yf:
        configuration_dict = yaml.safe_load(yf)
    validate_schema(configuration_dict)
    workflow_name = configuration_dict["workflow"]["name"]
    logger.debug(f"Workflow found: {workflow_name}")
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


def load_all():
    workflows = []
    for root, dirs, files in os.walk(Config.WORKFLOWS_CONFIG_PATH):
        for file in files:
            if file.endswith(".yml"):
                workflow_yaml_config_path = os.path.join(root, file)
                try:
                    workflow = load_one(workflow_yaml_config_path)
                    workflows.append(workflow)
                except Exception as error:
                    logger.error(error)
    return workflows
