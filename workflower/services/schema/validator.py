import logging
import os

from workflower.application.exceptions import (
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
    job_keys = ["name", "operator", "trigger"]
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


def job_operator_is_string_type(job_dict: dict) -> bool:
    """
    Validate job operator data type.
    """
    if not isinstance(job_dict["operator"], str):
        raise InvalidTypeError("Name must be type string")
    return True


def job_operator_options_in_expected(job_dict) -> bool:
    """
    Job operator must have expected options.
    """
    job_operator_options = ["alteryx", "papermill", "python", "module"]
    if job_dict["operator"] not in job_operator_options:
        raise InvalidSchemaError(
            f"Job operator options must be in: "
            f"{', '.join(job_operator_options)}"
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
    Validate Alteryx job operator.
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


def module_job_use_has_expected_keys(job_dict: dict) -> bool:
    """
    Module job must have expected keys.
    """
    module_keys = ["module_path", "module_name"]
    if not all(key in job_dict.keys() for key in module_keys):
        raise InvalidSchemaError(
            "Module jobs must contain: " f"{', '.join(module_keys)}"
        )
    return True


def module_job_path_is_file(job_dict: dict) -> bool:
    """
    Module job path must point to an existing file.
    """
    if not os.path.isfile(job_dict["module_path"]):
        raise InvalidFilePathError("Module path file not exists")
    return True


def module_job_paths_ends_with_yxmd(job_dict: dict) -> bool:
    """
    Module job paths must point to .yxmd type files.
    """
    if not job_dict["module_path"].endswith(".py"):
        raise InvalidTypeError("module_path must be .py file")
    return True


def validate_module_job(job_dict: dict) -> None:
    """
    Validate Module job operator.
    """
    module_job_use_has_expected_keys(job_dict)
    module_job_path_is_file(job_dict)
    module_job_paths_ends_with_yxmd(job_dict)


def validate_job_operator(job_dict: dict) -> None:
    """
    Validate job operator.
    """
    job_operator_is_string_type(job_dict)
    job_operator_options_in_expected(job_dict)
    # Papermill
    if job_dict["operator"] == "papermill":
        validate_papermill_job(job_dict)
    # Alteryx
    if job_dict["operator"] == "alteryx":
        validate_alteryx_job(job_dict)
    # Job triggers
    if job_dict["operator"] == "python":
        validate_python_job(job_dict)
    if job_dict["operator"] == "module":
        validate_module_job(job_dict)


def trigger_is_string_type(job_dict: dict) -> bool:
    """
    Trigger key value must be string type.
    """
    if not isinstance(job_dict["trigger"], str):
        raise InvalidTypeError("Name must be type string")
    return True


def job_trigger_has_expected_options(job_dict: dict) -> bool:
    """
    Job trigger must have expected options.
    """
    job_trigger_options = ["date", "cron", "interval", "dependency"]
    if job_dict["trigger"] not in job_trigger_options:
        raise InvalidSchemaError(
            f"Job trigger must be: {', '.join(job_trigger_options)}"
        )
    return True


def dependency_trigger_has_expected_keys(job_dict: dict) -> bool:
    """
    Dependency trigger must have expected keys.
    """
    dependency_options = ["depends_on"]
    if not all(key in job_dict.keys() for key in dependency_options):
        raise InvalidSchemaError(
            "Dependency triggered job must have keys: "
            f"{', '.join(dependency_options)}"
        )
    return True


def dependency_trigger_depends_on_existing_job(
    job_dict: dict,
    jobs_names: list,
) -> bool:
    """
    Dependency trigger depends_on must be an existing job.
    """
    if not job_dict["depends_on"] in jobs_names:
        raise InvalidSchemaError(
            "Job depends_on must have a valid job name reference "
            "from the same workflow"
        )
    return True


def validate_job_triggers(job_dict: dict, jobs_names: list) -> None:
    """
    Validate job triggers.
    """
    trigger_is_string_type(job_dict)
    job_trigger_has_expected_options(job_dict)
    if job_dict["trigger"] == "dependency":
        dependency_trigger_has_expected_keys(job_dict)
        dependency_trigger_depends_on_existing_job(job_dict, jobs_names)


def workflow_jobs_is_list_type(configuration_dict: dict) -> bool:
    """
    Workflow jobs must be string type.
    """
    workflow_jobs = configuration_dict["workflow"]["jobs"]
    if not isinstance(workflow_jobs, list):
        raise InvalidTypeError("Workflow jobs wrong definition")
    return True


def validate_workflow_jobs_definition(configuration_dict: dict) -> None:
    """
    Validate workflow jobs definition.
    """
    workflow_jobs_is_list_type(configuration_dict)
    workflow = configuration_dict["workflow"]
    workflow_jobs = workflow["jobs"]
    jobs_names = []
    for job in workflow_jobs:
        jobs_names.append(job["name"])
        job_name_is_string_type(job)
        job_has_expected_keys(job)
        #  Job operator
        validate_job_operator(job)


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
