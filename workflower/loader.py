import os

import yaml
from config import Config

from workflower.job import Job
from workflower.workflow import Workflow


def load_one(workflow_yaml_config_path):
    with open(workflow_yaml_config_path) as yf:
        configuration_dict = yaml.safe_load(yf)
        workflow_name = configuration_dict["workflow"]["name"]
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
    for root, dirs, files in os.walk(Config.WORKFLOWS_CONFIG_PATH):
        for file in files:
            if file.endswith(".yml"):
                workflow_yaml_config_path = os.path.join(root, file)
                workflow = load_one(workflow_yaml_config_path)
                yield workflow
