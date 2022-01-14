import logging
import os

from apscheduler.jobstores.base import ConflictingIdError
from papermill import execute_notebook

from workflower.alteryx import run_workflow

logger = logging.getLogger(__name__)


def prepare_date_trigger_options(configuration_dict: dict) -> dict:
    """
    Prepare a dict with date trigger options.
    """
    date_string_options = [
        "run_date",
        "timezone",
    ]

    date_string_options_dict = {
        date_option: str(configuration_dict.get(date_option))
        for date_option in date_string_options
        if configuration_dict.get(date_option)
    }
    return date_string_options_dict


def prepare_interval_trigger_options(configuration_dict: dict) -> dict:
    """
    Prepare a dict with interval trigger options.
    """
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
    return {**interval_int_options_dict, **interval_string_options_dict}


def prepare_cron_trigger_options(configuration_dict: dict) -> dict:
    """
    Prepare a dict with cron trigger options.
    """
    interval_int_or_string_options = [
        "year",
        "month",
        "day",
        "week",
        "day_of_week",
        "hours",
        "minutes",
        "seconds",
    ]
    interval_string_options = [
        "start_date",
        "end_date",
        "timezone",
    ]
    interval_int_options = [
        "jitter",
    ]
    interval_int_or_string_options_dict = {
        interval_option: configuration_dict.get(interval_option)
        for interval_option in interval_int_or_string_options
        if configuration_dict.get(interval_option)
        and (
            isinstance(configuration_dict.get(interval_option), int)
            or isinstance(configuration_dict.get(interval_option), str)
        )
    }
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
    return {
        **interval_int_or_string_options_dict,
        **interval_int_options_dict,
        **interval_string_options_dict,
    }


def get_trigger_options(configuration_dict: dict) -> dict:
    """
    Define trigger options from dict.
    """
    trigger_config = {}
    job_trigger = configuration_dict.get("trigger")
    logger.debug(f"Job trigger{job_trigger}")
    #  interval trigger
    if job_trigger == "interval":
        trigger_config.update(dict(trigger="interval"))
        interval_trigger_options = prepare_interval_trigger_options(
            configuration_dict
        )
        trigger_config.update(interval_trigger_options)
    #  Cron trigger
    elif job_trigger == "cron":
        trigger_config.update(dict(trigger="cron"))
        cron_trigger_options = prepare_cron_trigger_options(configuration_dict)
        trigger_config.update(cron_trigger_options)
    #  Date trigger
    elif job_trigger == "date":
        trigger_config.update(dict(trigger="date"))
        date_trigger_options = prepare_date_trigger_options(configuration_dict)
        trigger_config.update(date_trigger_options)
    return trigger_config


def get_job_uses(configuration_dict: dict) -> dict:
    """
    Define job uses from dict.
    """
    uses_config = {}
    job_uses = configuration_dict.get("uses")
    # Alteryx
    if job_uses == "alteryx":
        job_path = configuration_dict.get("path")
        if not os.path.isfile(job_path):
            logger.error("Not a valid job path")
        uses_config.update(dict(args=[job_path]))
        uses_config.update(dict(func=run_workflow))
    # Papermill
    if job_uses == "papermill":
        input_path = configuration_dict.get("input_path")
        if not os.path.isfile(input_path):
            logger.error("Not a valid job path")
        output_path = configuration_dict.get("output_path")
        uses_config.update(dict(func=execute_notebook))
        uses_config.update(
            dict(
                kwargs=dict(
                    input_path=input_path,
                    output_path=output_path,
                    log_output=True,
                    progress_bar=False,
                )
            )
        )

    return uses_config


def prepare(configuration_dict: dict) -> dict:
    # TODO
    # Verify and build job config
    # Maybe build a config file verifier on a web page with
    # file uploading and parsing.
    job_name = configuration_dict.get("name")
    job_executor = "default"
    job_config = {"id": job_name, "executor": job_executor}
    # Set job uses
    uses_options = get_job_uses(configuration_dict)
    job_config.update(uses_options)
    # Set job triggers
    trigger_options = get_trigger_options(configuration_dict)
    job_config.update(trigger_options)

    return job_config


def schedule_one(scheduler, configuration_dict: dict) -> None:
    """
    Schedule a job in apscheduler
    """
    job_config = prepare(configuration_dict)
    job_id = job_config["id"]
    logger.debug(f"scheduling {job_id}")
    # TODO
    # Move to another function
    # Update job if yaml file has been modified
    logger.debug(job_config)
    try:
        scheduler.add_job(**job_config)
    except ConflictingIdError:
        logger.warning(f"{job_id}, already scheduled")
