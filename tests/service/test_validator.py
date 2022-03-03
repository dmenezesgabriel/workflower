import unittest
import unittest.mock

import pytest
import workflower.services.schema.validator as validator
from workflower.application.exceptions import (
    InvalidFilePathError,
    InvalidSchemaError,
    InvalidTypeError,
)


class TestPipelineSchemaValidation:
    """
    Pipeline schema tests.
    """

    def test_pipeline_keys_valid_all_keys_ok(cls):
        """
        Pipeline keys must contain version and workflow.
        """
        dict_obj = {"version": "1.0", "workflow": {}}
        assert validator.pipeline_keys_valid(dict_obj) is True

    @pytest.mark.parametrize(
        "test_input", [({"workflow": {}}), ({"version": "1.0"})]
    )
    def test_pipeline_keys_valid_missing_keys(cls, test_input):
        """
        If pipeline not contain expected keys should raise Exception.
        """
        with pytest.raises(InvalidSchemaError):
            validator.pipeline_keys_valid(test_input)

    def test_version_is_string_type_true(cls):
        """
        Version must be string data type.
        """
        dict_obj = {"version": "1.0", "workflow": {}}
        assert validator.version_is_string_type(dict_obj) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"version": 1}),
            ({"version": 1.1}),
            ({"version": True}),
            ({"version": []}),
            ({"version": {}}),
            ({"version": ()}),
        ],
    )
    def test_version_is_string_type_not_string(cls, test_input):
        with pytest.raises(InvalidTypeError):
            validator.version_is_string_type(test_input)


class TestWorkflowSchemaValidation:
    """
    Workflow schema tests.
    """

    @pytest.fixture(scope="function")
    def workflow_dict(cls):
        return {
            "version": "1.0",
            "workflow": {"name": "workflow_name", "jobs": []},
        }

    def test_workflow_value_is_dict_type_true(cls, workflow_dict):
        """
        Workflow must be dict type.
        """
        assert validator.workflow_value_is_dict_type(workflow_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"workflow": 1}),
            ({"workflow": 1.1}),
            ({"workflow": True}),
            ({"workflow": []}),
            ({"workflow": ""}),
            ({"workflow": ()}),
        ],
    )
    def test_workflow_value_is_dict_type_not_dict(cls, test_input):
        with pytest.raises(InvalidTypeError):
            validator.workflow_value_is_dict_type(test_input)

    def test_workflow_has_expected_keys(cls, workflow_dict):
        """
        Workflow must have expected keys.
        """
        assert validator.workflow_has_expected_keys(workflow_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"workflow": {"name": "workflow_name"}}),
            ({"workflow": {"jobs": []}}),
        ],
    )
    def test_workflow_has_expected_keys_missing_keys(cls, test_input):
        """
        If Workflow not contain expected keys should raise Exception.
        """
        with pytest.raises(InvalidSchemaError):
            validator.workflow_has_expected_keys(test_input)

    def test_workflow_name_is_string_type_true(cls, workflow_dict):
        """
        Workflow must be dict type.
        """
        assert validator.workflow_name_is_string_type(workflow_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"version": "1.0", "workflow": {"name": 1}}),
            ({"version": "1.0", "workflow": {"name": 1.1}}),
            ({"version": "1.0", "workflow": {"name": True}}),
            ({"version": "1.0", "workflow": {"name": {}}}),
            ({"version": "1.0", "workflow": {"name": []}}),
            ({"version": "1.0", "workflow": {"name": ()}}),
        ],
    )
    def test_workflow_name_is_string_type_not_string(cls, test_input):
        with pytest.raises(InvalidTypeError):
            validator.workflow_name_is_string_type(test_input)

    def test_validate_workflow_definition_calls_workflow_value_check(
        cls, workflow_dict
    ):
        with unittest.mock.patch(
            "workflower.services.validator.workflow_value_is_dict_type"
        ) as mock:
            validator.validate_workflow_definition(workflow_dict)
        assert mock.call_count == 1

    def test_validate_workflow_definition_calls_workflow_keys_check(
        cls, workflow_dict
    ):
        with unittest.mock.patch(
            "workflower.services.validator.workflow_has_expected_keys"
        ) as mock:
            validator.validate_workflow_definition(workflow_dict)
        assert mock.call_count == 1

    def test_validate_workflow_definition_calls_workflow_name_check(
        cls, workflow_dict
    ):
        with unittest.mock.patch(
            "workflower.services.validator.workflow_name_is_string_type"
        ) as mock:
            validator.validate_workflow_definition(workflow_dict)
        assert mock.call_count == 1


class TestJobSchemaValidation:
    @pytest.fixture(scope="function")
    def job_dict(cls):
        return {"name": "job_name", "operator": "python", "trigger": "date"}

    def test_job_has_expected_keys(cls, job_dict):
        """
        Job must have expected keys.
        """
        assert validator.job_has_expected_keys(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"operator": "python", "trigger": "date"}),
            ({"name": "job_name", "trigger": "date"}),
            ({"name": "job_name", "operator": "python"}),
        ],
    )
    def test_job_has_expected_keys_missing_keys(cls, test_input):
        """
        If Job not contain expected keys should raise Exception.
        """
        with pytest.raises(InvalidSchemaError):
            validator.job_has_expected_keys(test_input)

    def test_job_name_is_string_type_true(cls, job_dict):
        """
        Job name must be string type.
        """
        assert validator.job_name_is_string_type(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"name": 1}),
            ({"name": 1.1}),
            ({"name": True}),
            ({"name": {}}),
            ({"name": []}),
            ({"name": ()}),
        ],
    )
    def test_job_name_is_string_type_not_string(cls, test_input):
        with pytest.raises(InvalidTypeError):
            validator.job_name_is_string_type(test_input)

    def test_job_operator_is_string_type_true(cls, job_dict):
        """
        Job operator must be dict type.
        """
        assert validator.job_operator_is_string_type(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"operator": 1}),
            ({"operator": 1.1}),
            ({"operator": True}),
            ({"operator": {}}),
            ({"operator": []}),
            ({"operator": ()}),
        ],
    )
    def test_job_operator_is_string_type_not_string(cls, test_input):
        with pytest.raises(InvalidTypeError):
            validator.job_operator_is_string_type(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"operator": "alteryx"}),
            ({"operator": "papermill"}),
            ({"operator": "python"}),
        ],
    )
    def test_job_operator_options_in_expected(cls, test_input):
        """
        Job operator must have expected options.
        """
        assert validator.job_operator_options_in_expected(test_input) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"operator": "altery"}),
            ({"operator": "papermil"}),
            ({"operator": "pyton"}),
        ],
    )
    def test_job_operator_options_in_expected_not_in_expected(cls, test_input):
        """
        Job operator must have expected options.
        """
        with pytest.raises(InvalidSchemaError):
            validator.job_operator_options_in_expected(test_input)

    def test_validate_job_operator(cls):
        # TODO
        # Implement this
        pass


class TestPapermillJobSchemaValidation:
    """
    Papermill operator schema validation.
    """

    @pytest.fixture(scope="function")
    def jupyter_notebook_file(cls, tmpdir_factory):
        """
        Return a function that creates a temporary jupyter notebook
        with given name.
        """

        def _return_notebook_path(name):
            """
            Return a Jupyter notebook mock file.
            """
            file_content = """
            {
            "cells": [
            {
            "cell_type": "code",
            "execution_count": null,
            "metadata": {},
            "outputs": [],
            "source": [
                "print(\"Hello, World!\")"
            ]
            }
            ],
            "metadata": {
            "interpreter": {
            "hash": "123"
            },
            "kernelspec": {
            "display_name": "Python 3.10.0 64-bit ('venv': venv)",
            "language": "python",
            "name": "python3"
            },
            "language_info": {
            "name": "python",
            "version": "3.10.0"
            },
            "orig_nbformat": 4
            },
            "nbformat": 4,
            "nbformat_minor": 2
            }
            """
            p = tmpdir_factory.mktemp("file").join(name)
            p.write_text(file_content, encoding="utf-8")
            return p

        return _return_notebook_path

    @pytest.fixture(scope="function")
    def job_dict(cls, jupyter_notebook_file):
        return {
            "name": "job_name",
            "operator": "papermill",
            "trigger": "interval",
            "minutes": 1,
            "input_path": str(jupyter_notebook_file(name="notebook.ipynb")),
            "output_path": str(
                jupyter_notebook_file(name="notebook_output.ipynb")
            ),
        }

    def test_papermill_job_use_has_expected_keys(cls, job_dict):
        """
        Job must have expected keys.
        """
        assert validator.papermill_job_use_has_expected_keys(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            (
                {
                    "name": "job_name",
                    "operator": "papermill",
                    "trigger": "date",
                    "input_path": "",
                }
            ),
            (
                {
                    "name": "job_name",
                    "operator": "papermill",
                    "trigger": "date",
                    "output_path": "",
                }
            ),
            (
                {
                    "name": "job_name",
                    "operator": "papermill",
                    "trigger": "date",
                }
            ),
        ],
    )
    def test_papermill_job_use_has_expected_keys_missing_keys(cls, test_input):
        """
        If Job not contain expected keys should raise Exception.
        """
        with pytest.raises(InvalidSchemaError):
            validator.papermill_job_use_has_expected_keys(test_input)

    def test_papermill_job_input_path_is_file(cls, job_dict):
        """
        Papermill input_path must be an existing file.
        """
        assert validator.papermill_job_input_path_is_file(job_dict) is True

    def test_papermill_job_input_path_is_file_not_exists(cls):
        """
        Papermill input_path must be an existing file.
        """
        job_dict = {"input_path": "./test.ipynb"}
        with pytest.raises(InvalidFilePathError):
            validator.papermill_job_input_path_is_file(job_dict)

    def test_papermill_job_paths_ends_with_ipynb_true(cls, job_dict):
        """
        Papermill job paths must point to .ipynb type files.
        """
        assert validator.papermill_job_paths_ends_with_ipynb(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            (
                {
                    "name": "job_name",
                    "operator": "papermill",
                    "trigger": "interval",
                    "minutes": 1,
                    "input_path": "./test.txt",
                    "output_path": "./test.ipynb",
                }
            ),
            (
                {
                    "name": "job_name",
                    "operator": "papermill",
                    "trigger": "interval",
                    "minutes": 1,
                    "input_path": "./test.ipynb",
                    "output_path": "./test.txt",
                }
            ),
        ],
    )
    def test_papermill_job_paths_ends_with_ipynb_false(cls, test_input):
        """
        Papermill job paths must point to .ipynb type files.
        """
        with pytest.raises(InvalidTypeError):
            validator.papermill_job_paths_ends_with_ipynb(test_input)

    def test_validate_papermill_job_calls_papermill_job_use_has_expected_keys(
        cls, job_dict
    ):
        with unittest.mock.patch(
            "workflower.services.validator.papermill_job_use_has_expected_keys"
        ) as mock:
            validator.validate_papermill_job(job_dict)
        assert mock.call_count == 1

    def test_validate_papermill_job_calls_papermill_job_input_path_is_file(
        cls, job_dict
    ):
        with unittest.mock.patch(
            "workflower.services.validator.papermill_job_input_path_is_file"
        ) as mock:
            validator.validate_papermill_job(job_dict)
        assert mock.call_count == 1

    def test_validate_papermill_job_calls_papermill_job_paths_ends_with_ipynb(
        cls, job_dict
    ):
        with unittest.mock.patch(
            "workflower.services.validator.papermill_job_paths_ends_with_ipynb"
        ) as mock:
            validator.validate_papermill_job(job_dict)
        assert mock.call_count == 1


class TestAlteryxJobSchemaValidation:
    """
    Alteryx operator schema validation.
    """

    @pytest.fixture(scope="function")
    def alteryx_workflow_file(cls, tmpdir_factory) -> str:
        """
        Return Alteryx workflow mocked file.
        """
        file_content = """
        xml stuff
        """
        p = tmpdir_factory.mktemp("file").join("workflow.yxmd")
        p.write_text(file_content, encoding="utf-8")
        return str(p)

    @pytest.fixture(scope="function")
    def job_dict(cls, alteryx_workflow_file):
        return {
            "name": "job_name",
            "operator": "alteryx",
            "path": alteryx_workflow_file,
            "trigger": "interval",
            "minutes": 1,
        }

    def test_alteryx_job_use_has_expected_keys(cls, job_dict):
        """
        Job must have expected keys.
        """
        assert validator.alteryx_job_use_has_expected_keys(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            (
                {
                    "name": "job_name",
                    "operator": "alteryx",
                    "trigger": "date",
                }
            ),
        ],
    )
    def test_alteryx_job_use_has_expected_keys_missing_keys(cls, test_input):
        """
        If Job not contain expected keys should raise Exception.
        """
        with pytest.raises(InvalidSchemaError):
            validator.alteryx_job_use_has_expected_keys(test_input)

    def test_alteryx_job_path_is_file(cls, job_dict):
        """
        Alteryx path must be an existing file.
        """
        assert validator.alteryx_job_path_is_file(job_dict) is True

    def test_alteryx_job_path_is_file_not_exists(cls):
        """
        Alteryx path must be an existing file.
        """
        job_dict = {"path": "./test.yxmd"}
        with pytest.raises(InvalidFilePathError):
            validator.alteryx_job_path_is_file(job_dict)

    def test_alteryx_job_paths_ends_with_yxmd_true(cls, job_dict):
        """
        Alteryx job paths must point to .yxmd type files.
        """
        assert validator.alteryx_job_paths_ends_with_yxmd(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            (
                {
                    "name": "job_name",
                    "operator": "alteryx",
                    "trigger": "interval",
                    "minutes": 1,
                    "path": "./test.txt",
                }
            ),
        ],
    )
    def test_alteryx_job_paths_ends_with_yxmd_false(cls, test_input):
        """
        Alteryx job paths must point to .yxmd type files.
        """
        with pytest.raises(InvalidTypeError):
            validator.alteryx_job_paths_ends_with_yxmd(test_input)

    def test_validate_alteryx_job_calls_alteryx_job_use_has_expected_keys(
        cls, job_dict
    ):
        with unittest.mock.patch(
            "workflower.services.validator.alteryx_job_use_has_expected_keys"
        ) as mock:
            validator.validate_alteryx_job(job_dict)
        assert mock.call_count == 1

    def test_validate_alteryx_job_calls_alteryx_job_path_is_file(
        cls, job_dict
    ):
        with unittest.mock.patch(
            "workflower.services.validator.alteryx_job_path_is_file"
        ) as mock:
            validator.validate_alteryx_job(job_dict)
        assert mock.call_count == 1

    def test_validate_alteryx_job_calls_alteryx_job_paths_ends_with_yxmd(
        cls, job_dict
    ):
        with unittest.mock.patch(
            "workflower.services.validator.alteryx_job_paths_ends_with_yxmd"
        ) as mock:
            validator.validate_alteryx_job(job_dict)
        assert mock.call_count == 1


class TestPythonJobSchemaValidation:
    pass
