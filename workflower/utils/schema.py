import logging
import os

from workflower.exceptions import InvalidSchemaError, InvalidTypeError

logger = logging.getLogger("workflower.utils.schema")


# Pipeline
def pipeline_keys_valid(configuration_dict: dict) -> bool:
    """
    Dict must have version and workflow keys.
    """
    pipeline_keys = ["version", "workflow"]
    if not all(key in configuration_dict.keys() for key in pipeline_keys):
        raise InvalidSchemaError(
            "The pipeline must have all of it's keys: "
            f"{', '.join(pipeline_keys)}"
        )
    return True


def version_is_string_type(configuration_dict: dict) -> bool:
    """
    Version key value must be string type.
    """
    if not isinstance(configuration_dict["version"], str):
        raise InvalidTypeError("Version must be type string")
    return True


#  Workflow
def workflow_value_is_dict_type(configuration_dict: dict) -> bool:
    """
    Workflow key value must be dict type.
    """
    if not isinstance(configuration_dict["workflow"], dict):
        raise InvalidTypeError("Workflow wrong definition")
    return True


def workflow_has_expected_keys(configuration_dict: dict) -> bool:
    """
    Workflow must have expected keys.
    """
    workflow_keys = ["name", "jobs"]
    workflow = configuration_dict["workflow"]
    if not all(key in workflow.keys() for key in workflow_keys):
        raise InvalidSchemaError(
            "The workflow must have all of it's keys: "
            f"{', '.join(workflow_keys)}"
        )
    return True


def workflow_name_is_string_type(configuration_dict: dict) -> bool:
    """
    Workflow name value must be string data type.
    """
    workflow = configuration_dict["workflow"]
    if not isinstance(workflow["name"], str):
        raise InvalidTypeError("Name must be type string")
    return True


def validate_workflow_definition(configuration_dict: dict) -> None:
    """
    Validate workflow definition.
    """
    workflow_value_is_dict_type(configuration_dict)
    workflow_has_expected_keys(configuration_dict)
    workflow_name_is_string_type(configuration_dict)


# Jobs
def job_has_expected_keys(job_dict: dict) -> bool:
    """
    Validate job attributes.
    """
    job_keys = ["name", "uses", "trigger"]
    if not all(key in job_dict.keys() for key in job_keys):
        raise InvalidSchemaError(
            "The job must have all of it's keys: " f"{', '.join(job_keys)}"
        )
    return True


def job_name_is_string_type(job_dict: dict) -> bool:
    """
    Validate job name data type.
    """
    if not isinstance(job_dict["name"], str):
        raise InvalidTypeError("Name must be type string")
    return True


def job_uses_is_string_type(job_dict: dict) -> bool:
    """
    Validate job uses data type.
    """
    if not isinstance(job_dict["uses"], str):
        raise InvalidTypeError("Name must be type string")
    return True


def job_uses_options_in_expected(job_dict) -> bool:
    """
    Job uses must have expected options.
    """
    job_uses_options = ["alteryx", "papermill", "python"]
    if job_dict["uses"] not in job_uses_options:
        raise InvalidSchemaError(
            f"Job uses options must be in: {', '.join(job_uses_options)}"
        )
    return True


def papermill_job_use_has_expected_keys(job_dict: dict) -> bool:
    papermill_keys = ["input_path", "output_path"]
    if not all(key in job_dict.keys() for key in papermill_keys):
        raise InvalidSchemaError(
            "Papermill jobs must contain: " f"{', '.join(papermill_keys)}"
        )
    return True


def validate_papermill_job(job_dict: dict) -> None:
    papermill_job_use_has_expected_keys(job_dict)
    # TODO
    # Validate if input_path ends with ipynb and file exists
    # and output_path ends with ipynb and dir exists


def validate_alteryx_job(job_dict: dict) -> None:
    alteryx_keys = ["path"]
    if not all(key in job_dict.keys() for key in alteryx_keys):
        raise InvalidSchemaError(
            "Alteryx jobs must contain: " f"{', '.join(alteryx_keys)}"
        )
    # TODO
    # Validate if path ends with alteryx extension and file exists


def validate_python_job(job_dict: dict) -> None:
    python_keys = ["code", "script_path"]
    if not any(key in job_dict.keys() for key in python_keys):
        raise InvalidSchemaError(
            "Python jobs must contain any of: " f"{', '.join(python_keys)}"
        )


def validate_job_uses(job_dict: dict) -> None:
    """
    Validate job uses.
    """
    job_uses_is_string_type(job_dict)
    job_uses_options_in_expected(job_dict)
    # Papermill
    if job_dict["uses"] == "papermill":
        validate_papermill_job(job_dict)
    # Alteryx
    if job_dict["uses"] == "alteryx":
        validate_alteryx_job(job_dict)
    # Job triggers
    if job_dict["uses"] == "python":
        validate_python_job(job_dict)


def validate_job_triggers(job_dict: dict, jobs_names: list) -> None:
    """
    Validate job triggers.
    """
    job_trigger_options = ["date", "cron", "interval", "dependency"]
    if not isinstance(job_dict["trigger"], str):
        raise InvalidTypeError("Name must be type string")
    if job_dict["trigger"] not in job_trigger_options:
        raise InvalidSchemaError(
            f"Job trigger must be: {', '.join(job_trigger_options)}"
        )
    if job_dict["trigger"] == "dependency":
        dependency_options = ["depends_on"]
        if not all(key in job_dict.keys() for key in dependency_options):
            raise InvalidSchemaError(
                "Dependency triggered job must have keys: "
                f"{', '.join(dependency_options)}"
            )
        if not job_dict["depends_on"] in jobs_names:
            raise InvalidSchemaError(
                "Job depends_on must have a valid job name reference "
                "from the same workflow"
            )


def validate_workflow_jobs_definition(configuration_dict: dict) -> None:
    """
    Validate workflow jobs definition.
    """
    workflow = configuration_dict["workflow"]
    workflow_jobs = workflow["jobs"]
    if not isinstance(workflow_jobs, list):
        raise InvalidTypeError("Workflow jobs wrong definition")
    jobs_names = []
    for job in workflow_jobs:
        jobs_names.append(job["name"])
        job_name_is_string_type(job)
        job_has_expected_keys(job)
        #  Job uses
        validate_job_uses(job)


def validate_schema(configuration_dict: dict) -> bool:
    """
    Validate pipeline file schema
    """
    logger.debug("Validating yml schema")
    #  Pipeline
    pipeline_keys_valid(configuration_dict)
    version_is_string_type(configuration_dict)
    #  Workflow
    validate_workflow_definition(configuration_dict)
    # Jobs
    validate_workflow_jobs_definition(configuration_dict)
    return True


# Parse jobs
def parse_job_date_trigger_options(configuration_dict) -> dict:
    """
    parse_job a dict with date trigger options.
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


def parse_job_interval_trigger_options(configuration_dict) -> dict:
    """
    parse_job a dict with interval trigger options.
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


def parse_job_cron_trigger_options(configuration_dict) -> dict:
    """
    parse_job a dict with cron trigger options.
    """
    interval_int_or_string_options = [
        "year",
        "month",
        "day",
        "week",
        "day_of_week",
        "hour",
        "minute",
        "second",
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


def parse_job_trigger_options(configuration_dict) -> dict:
    """
    Define trigger options from dict.
    """
    trigger_config = {}
    job_trigger = configuration_dict.get("trigger")
    logger.debug(f"Job trigger {job_trigger}")
    #  interval trigger
    if job_trigger == "interval":
        trigger_config.update(dict(trigger="interval"))
        interval_trigger_options = parse_job_interval_trigger_options(
            configuration_dict
        )
        trigger_config.update(interval_trigger_options)
    #  Cron trigger
    elif job_trigger == "cron":
        trigger_config.update(dict(trigger="cron"))
        cron_trigger_options = parse_job_cron_trigger_options(
            configuration_dict
        )
        trigger_config.update(cron_trigger_options)
    #  Date trigger
    elif job_trigger == "date":
        trigger_config.update(dict(trigger="date"))
        date_trigger_options = parse_job_date_trigger_options(
            configuration_dict
        )
        trigger_config.update(date_trigger_options)
    elif job_trigger == "dependency":
        # Trigger "dependency" is not recognized by apscheduler, so it must be
        # removed from job definition
        configuration_dict.pop("trigger", None)
    return trigger_config


def parse_job_uses(configuration_dict) -> dict:
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
        uses_config.update(dict(func="AlteryxOperator.execute"))
    # Papermill
    if job_uses == "papermill":
        input_path = configuration_dict.get("input_path")
        if not os.path.isfile(input_path):
            logger.error("Not a valid job path")
        output_path = configuration_dict.get("output_path")
        uses_config.update(dict(func="PapermillOperator.execute"))
        uses_config.update(
            dict(
                kwargs=dict(
                    input_path=input_path,
                    output_path=output_path,
                )
            )
        )
    # Python
    if job_uses == "python":
        script_path = configuration_dict.get("script_path")
        code = configuration_dict.get("code")
        requirements_path = configuration_dict.get("requirements_path")
        uses_dict = {"kwargs": {}}
        if script_path:
            if not os.path.isfile(script_path):
                logger.error("Not a valid python script path")
            uses_dict["kwargs"].update(dict(script_path=script_path))
        elif code:
            uses_dict["kwargs"].update(dict(code=code))
        if requirements_path:
            if not os.path.isfile(requirements_path):
                logger.error("Not a valid requirements path")
            uses_config.update(
                uses_dict["kwargs"].update(
                    dict(requirements_path=requirements_path)
                )
            )
        uses_dict.update(dict(func="PythonOperator.execute"))
        uses_config.update(uses_dict)
    return uses_config


def make_job_definition(configuration_dict) -> dict:
    # TODO
    # Verify and build job config
    # Maybe build a config file verifier on a web page with
    # file uploading and parsing.
    job_name = configuration_dict.get("name")
    job_executor = "default"
    job_config = {"id": job_name, "executor": job_executor}
    # Set job uses
    uses_options = parse_job_uses(configuration_dict)
    job_config.update(uses_options)
    # Set job triggers
    trigger_options = parse_job_trigger_options(configuration_dict)
    job_config.update(trigger_options)

    return job_config
