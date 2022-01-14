import os

from apscheduler.jobstores.base import ConflictingIdError

from workflower.alteryx import run_workflow


def get_trigger_options(configuration_dict):
    trigger_config = {}
    job_trigger = configuration_dict.get("trigger")
    if job_trigger == "interval":
        interval_int_options = [
            "weeks",
            "days",
            "hours",
            "minutes",
            "seconds",
            "jitter",
        ]

        interval_string_options = [
            "start_date",
            "end_date",
            "timezone",
        ]
        interval_int_options_dict = {
            interval_option: int(configuration_dict.get(interval_option))
            for interval_option in interval_int_options
            if configuration_dict.get(interval_option)
        }
        interval_string_options_dict = {
            interval_option: str(configuration_dict.get(interval_option))
            for interval_option in interval_string_options
            if configuration_dict.get(interval_option)
        }
        trigger_config.update(dict(trigger="interval"))
        trigger_config.update(interval_int_options_dict)
        trigger_config.update(interval_string_options_dict)
        return trigger_config


def get_job_uses(configuration_dict):
    uses_config = {}
    job_uses = configuration_dict.get("uses")

    if job_uses in ["alteryx", "jupyter", "knime"]:
        job_path = configuration_dict.get("path")
        if not os.path.isfile(job_path):
            print("Not a valid job path")
        uses_config.update(dict(args=[job_path]))

    if job_uses == "alteryx":
        uses_config.update(dict(func=run_workflow))

    return uses_config


def prepare(configuration_dict: dict) -> dict:
    # TODO
    # Verify and build job config
    # Maybe build a config file verifier on a web page with
    # file uploading and parsing.
    job_name = configuration_dict.get("name")

    job_config = {"id": job_name, "executor": "default"}
    trigger_options = get_trigger_options(configuration_dict)
    job_config.update(trigger_options)
    uses_options = get_job_uses(configuration_dict)
    job_config.update(uses_options)
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
