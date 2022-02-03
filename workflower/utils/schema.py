import logging
import os

from workflower.config import Config
from workflower.exceptions import (
    InvalidFilePathError,
    InvalidSchemaError,
    InvalidTypeError,
)

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
    """
    papermill job must have expected keys.
    """
    papermill_keys = ["input_path", "output_path"]
    if not all(key in job_dict.keys() for key in papermill_keys):
        raise InvalidSchemaError(
            "Papermill jobs must contain: " f"{', '.join(papermill_keys)}"
        )
    return True


def papermill_job_input_path_is_file(job_dict: dict) -> bool:
    """
    Papermill job input_path must point to an existing file.
    """
    if not os.path.isfile(job_dict["input_path"]):
        raise InvalidFilePathError("Papermill input_path file not exists")
    return True


def papermill_job_paths_ends_with_ipynb(job_dict: dict) -> bool:
    """
    Papermill job paths must point to .ipynb type files.
    """
    if not job_dict["input_path"].endswith(".ipynb") or not job_dict[
        "output_path"
    ].endswith(".ipynb"):
        raise InvalidTypeError("input and output paths must be .ipynb files")
    return True


def validate_papermill_job(job_dict: dict) -> None:
    """
    Validate papermill job use.
    """
    papermill_job_use_has_expected_keys(job_dict)
    papermill_job_input_path_is_file(job_dict)
    papermill_job_paths_ends_with_ipynb(job_dict)


def alteryx_job_use_has_expected_keys(job_dict: dict) -> bool:
    """
    Alteryx job must have expected keys.
    """
    alteryx_keys = ["path"]
    if not all(key in job_dict.keys() for key in alteryx_keys):
        raise InvalidSchemaError(
            "Alteryx jobs must contain: " f"{', '.join(alteryx_keys)}"
        )
    return True


def alteryx_job_path_is_file(job_dict: dict) -> bool:
    """
    Alteryx job path must point to an existing file.
    """
    if not os.path.isfile(job_dict["path"]):
        raise InvalidFilePathError("Alteryx path file not exists")
    return True


def alteryx_job_paths_ends_with_yxmd(job_dict: dict) -> bool:
    """
    Alteryx job paths must point to .yxmd type files.
    """
    if not job_dict["path"].endswith(".yxmd"):
        raise InvalidTypeError("path paths must be .yxmd file")
    return True


def validate_alteryx_job(job_dict: dict) -> None:
    """
    Validate Alteryx job uses.
    """
    alteryx_job_use_has_expected_keys(job_dict)
    alteryx_job_path_is_file(job_dict)
    alteryx_job_paths_ends_with_yxmd(job_dict)


def python_job_use_has_expected_keys(job_dict: dict) -> bool:
    """
    Python job must have expected keys.
    """
    python_keys = ["code", "script_path"]
    if not any(key in job_dict.keys() for key in python_keys):
        raise InvalidSchemaError(
            "Python jobs must contain any of: " f"{', '.join(python_keys)}"
        )
    return True


def validate_python_job(job_dict: dict) -> None:
    python_job_use_has_expected_keys(job_dict)


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


class PipelineSchemaParser:
    """
    Pipeline Schema parser.
    """

    pass


class WorkflowSchemaParser:
    """
    Workflow Schema parser.
    """

    pass


class JobSchemaParser:
    """
    Job Schema parser.
    """

    def __init__(self):
        self.schema_args = []
        self.schema_kwargs = {}
        self.trigger_config = {}
        self.uses_config = {}

    def parse_job_date_trigger_options(self, configuration_dict) -> dict:
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

    def parse_job_interval_trigger_options(self, configuration_dict) -> dict:
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

    def parse_job_cron_trigger_options(self, configuration_dict) -> dict:
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

    def parse_job_trigger_options(self, configuration_dict) -> None:
        """
        Define trigger options from dict.
        """
        job_trigger = configuration_dict.get("trigger")
        logger.debug(f"Job trigger {job_trigger}")
        #  interval trigger
        if job_trigger == "interval":
            self.trigger_config.update(dict(trigger="interval"))
            interval_trigger_options = self.parse_job_interval_trigger_options(
                configuration_dict
            )
            self.trigger_config.update(interval_trigger_options)
        #  Cron trigger
        elif job_trigger == "cron":
            self.trigger_config.update(dict(trigger="cron"))
            cron_trigger_options = self.parse_job_cron_trigger_options(
                configuration_dict
            )
            self.trigger_config.update(cron_trigger_options)
        #  Date trigger
        elif job_trigger == "date":
            self.trigger_config.update(dict(trigger="date"))
            date_trigger_options = self.parse_job_date_trigger_options(
                configuration_dict
            )
            self.trigger_config.update(date_trigger_options)
        elif job_trigger == "dependency":
            # Trigger "dependency" is not recognized by apscheduler, so it
            # must be removed from job definition
            configuration_dict.pop("trigger", None)

    def parse_job_uses(self, configuration_dict) -> dict:
        """
        Define job uses from dict.
        """
        job_uses = configuration_dict.get("uses")
        # Alteryx
        if job_uses == "alteryx":
            workflow_file_path = configuration_dict.get("path")
            if not os.path.isfile(workflow_file_path):
                logger.error("Not a valid job path")
            self.schema_kwargs.update(
                dict(workflow_file_path=workflow_file_path)
            )
            self.uses_config.update(dict(func="AlteryxOperator.execute"))
        # Papermill
        elif job_uses == "papermill":
            input_path = configuration_dict.get("input_path")
            if not os.path.isfile(input_path):
                logger.error("Not a valid job path")
            output_path = configuration_dict.get("output_path")
            self.uses_config.update(dict(func="PapermillOperator.execute"))
            self.schema_kwargs.update(
                dict(
                    input_path=input_path,
                    output_path=output_path,
                    environments_dir=Config.ENVIRONMENTS_DIR,
                    kernel_specs_dir=Config.KERNELS_SPECS_DIR,
                    pip_index_url=Config.PIP_INDEX_URL,
                    pip_trusted_host=Config.PIP_TRUSTED_HOST,
                )
            )
        # Python
        elif job_uses == "python":
            script_path = configuration_dict.get("script_path")
            code = configuration_dict.get("code")
            requirements_path = configuration_dict.get("requirements_path")
            if code:
                self.schema_kwargs.update(dict(code=code))
            elif script_path:
                if not os.path.isfile(script_path):
                    logger.error("Not a valid python script path")
                self.schema_kwargs.update(dict(script_path=script_path))
            if requirements_path:
                if not os.path.isfile(requirements_path):
                    logger.error("Not a valid requirements path")
                self.schema_kwargs.update(
                    dict(requirements_path=requirements_path)
                )
            self.schema_kwargs.update(
                dict(
                    pip_index_url=Config.PIP_INDEX_URL,
                    pip_trusted_host=Config.PIP_TRUSTED_HOST,
                    environments_dir=Config.ENVIRONMENTS_DIR,
                )
            )
            self.uses_config.update(dict(func="PythonOperator.execute"))

    def parse_schema(self, configuration_dict):
        job_name = configuration_dict.get("name")
        job_executor = "default"
        job_config = {"id": job_name, "executor": job_executor}
        self.parse_job_trigger_options(configuration_dict)
        self.parse_job_uses(configuration_dict)
        #  Update job config
        logger.debug(f"Job schema args: {self.schema_args}")
        if self.schema_args:
            job_config.update(dict(args=self.schema_args))
        logger.debug(f"Job schema kwargs: {self.schema_kwargs}")
        if self.schema_kwargs:
            job_config.update(dict(kwargs=self.schema_kwargs))
        logger.debug(f"Job schema trigger: {self.trigger_config}")
        if self.trigger_config:
            job_config.update(self.trigger_config)
        logger.debug(f"Job schema uses: {self.uses_config}")
        if self.uses_config:
            job_config.update(self.uses_config)
        logger.debug(f"job parsed configuration: {job_config}")
        return job_config
