import os

from workflower.alteryx import run_workflow


def load(configuration_dict: dict) -> dict:
    # TODO
    # Verify and build job config
    # Maybe build a config file verifier on a web page with
    # file uploading and parsing.
    workflow_name = configuration_dict["name"]
    workflow_path = configuration_dict["path"]
    if not os.path.isfile(workflow_path):
        print("Not a valid workflow path")

    job_config = {
        "func": run_workflow,
        "trigger": "interval",
        "id": workflow_name,
        "args": [workflow_path],
        "executor": "default",
        "minutes": 1,
    }
    return job_config


def schedule(configuration_dict):
    pass
