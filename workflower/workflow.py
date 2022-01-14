from workflower.job import schedule_one


def schedule_jobs(scheduler, configuration_dict: dict) -> dict:
    workflow_name = configuration_dict["workflow"]["name"]
    workflow_jobs = configuration_dict["workflow"]["jobs"]
    for job_configuration_dict in workflow_jobs:
        job_name = job_configuration_dict["name"]
        new_job_name = workflow_name + "_" + job_name
        job_configuration_dict.update({"name": new_job_name})
        schedule_one(scheduler, job_configuration_dict)
