import os

from apscheduler.jobstores.base import ConflictingIdError

from workflower.alteryx import run_workflow


def prepare(configuration_dict: dict) -> dict:
    # TODO
    # Verify and build job config
    # Maybe build a config file verifier on a web page with
    # file uploading and parsing.
    job_uses = configuration_dict.get("uses")
    job_name = configuration_dict.get("name")
    job_path = configuration_dict.get("path")
    job_trigger = configuration_dict.get("trigger")
    job_config = {"id": job_name, "executor": "default"}

    if job_uses == "alteryx":
        job_config.update(dict(func=run_workflow, args=[job_path]))

    if not os.path.isfile(job_path):
        print("Not a valid job path")

    if job_trigger == "interval":
        interval_options = [
            "weeks",
            "days",
            "hours",
            "minutes",
            "seconds",
            "start_date",
            "end_date",
            "timezone",
            "jitter",
        ]
        interval_options_dict = {
            interval_option: configuration_dict.get(interval_option)
            for interval_option in interval_options
            if configuration_dict.get(interval_option)
        }
        job_config.update(dict(trigger="interval"))
        job_config.update(interval_options_dict)

    return job_config


def schedule_one(scheduler, configuration_dict):
    job_config = prepare(configuration_dict)
    job_id = job_config["id"]
    print(f"scheduling {job_id}")
    # TODO
    # Move to another function
    # Update job if yaml file has been modified
    try:
        scheduler.add_job(**job_config)
    except ConflictingIdError:

        print(f"{job_id}, already scheduled")
