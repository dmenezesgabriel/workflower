import unittest
import unittest.mock

import pytest
import workflower.utils.schema as schema
from workflower.exceptions import (
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
        assert schema.pipeline_keys_valid(dict_obj) is True

    @pytest.mark.parametrize(
        "test_input", [({"workflow": {}}), ({"version": "1.0"})]
    )
    def test_pipeline_keys_valid_missing_keys(cls, test_input):
        """
        If pipeline not contain expected keys should raise Exception.
        """
        with pytest.raises(InvalidSchemaError):
            schema.pipeline_keys_valid(test_input)

    def test_version_is_string_type_true(cls):
        """
        Version must be string data type.
        """
        dict_obj = {"version": "1.0", "workflow": {}}
        assert schema.version_is_string_type(dict_obj) is True

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
            schema.version_is_string_type(test_input)


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
        assert schema.workflow_value_is_dict_type(workflow_dict) is True

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
            schema.workflow_value_is_dict_type(test_input)

    def test_workflow_has_expected_keys(cls, workflow_dict):
        """
        Workflow must have expected keys.
        """
        assert schema.workflow_has_expected_keys(workflow_dict) is True

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
            schema.workflow_has_expected_keys(test_input)

    def test_workflow_name_is_string_type_true(cls, workflow_dict):
        """
        Workflow must be dict type.
        """
        assert schema.workflow_name_is_string_type(workflow_dict) is True

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
            schema.workflow_name_is_string_type(test_input)

    def test_validate_workflow_definition_calls_workflow_value_check(
        cls, workflow_dict
    ):
        with unittest.mock.patch(
            "workflower.utils.schema.workflow_value_is_dict_type"
        ) as mock:
            schema.validate_workflow_definition(workflow_dict)
        assert mock.call_count == 1

    def test_validate_workflow_definition_calls_workflow_keys_check(
        cls, workflow_dict
    ):
        with unittest.mock.patch(
            "workflower.utils.schema.workflow_has_expected_keys"
        ) as mock:
            schema.validate_workflow_definition(workflow_dict)
        assert mock.call_count == 1

    def test_validate_workflow_definition_calls_workflow_name_check(
        cls, workflow_dict
    ):
        with unittest.mock.patch(
            "workflower.utils.schema.workflow_name_is_string_type"
        ) as mock:
            schema.validate_workflow_definition(workflow_dict)
        assert mock.call_count == 1


class TestJobSchemaValidation:
    @pytest.fixture(scope="function")
    def job_dict(cls):
        return {"name": "job_name", "uses": "python", "trigger": "date"}

    def test_job_has_expected_keys(cls, job_dict):
        """
        Job must have expected keys.
        """
        assert schema.job_has_expected_keys(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"uses": "python", "trigger": "date"}),
            ({"name": "job_name", "trigger": "date"}),
            ({"name": "job_name", "uses": "python"}),
        ],
    )
    def test_job_has_expected_keys_missing_keys(cls, test_input):
        """
        If Job not contain expected keys should raise Exception.
        """
        with pytest.raises(InvalidSchemaError):
            schema.job_has_expected_keys(test_input)

    def test_job_name_is_string_type_true(cls, job_dict):
        """
        Job name must be string type.
        """
        assert schema.job_name_is_string_type(job_dict) is True

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
            schema.job_name_is_string_type(test_input)

    def test_job_uses_is_string_type_true(cls, job_dict):
        """
        Job uses must be dict type.
        """
        assert schema.job_uses_is_string_type(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"uses": 1}),
            ({"uses": 1.1}),
            ({"uses": True}),
            ({"uses": {}}),
            ({"uses": []}),
            ({"uses": ()}),
        ],
    )
    def test_job_uses_is_string_type_not_string(cls, test_input):
        with pytest.raises(InvalidTypeError):
            schema.job_uses_is_string_type(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"uses": "alteryx"}),
            ({"uses": "papermill"}),
            ({"uses": "python"}),
        ],
    )
    def test_job_uses_options_in_expected(cls, test_input):
        """
        Job uses must have expected options.
        """
        assert schema.job_uses_options_in_expected(test_input) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            ({"uses": "altery"}),
            ({"uses": "papermil"}),
            ({"uses": "pyton"}),
        ],
    )
    def test_job_uses_options_in_expected_not_in_expected(cls, test_input):
        """
        Job uses must have expected options.
        """
        with pytest.raises(InvalidSchemaError):
            schema.job_uses_options_in_expected(test_input)

    def test_validate_job_uses(cls):
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
            "uses": "papermill",
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
        assert schema.papermill_job_use_has_expected_keys(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            (
                {
                    "name": "job_name",
                    "uses": "papermill",
                    "trigger": "date",
                    "input_path": "",
                }
            ),
            (
                {
                    "name": "job_name",
                    "uses": "papermill",
                    "trigger": "date",
                    "output_path": "",
                }
            ),
            (
                {
                    "name": "job_name",
                    "uses": "papermill",
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
            schema.papermill_job_use_has_expected_keys(test_input)

    def test_papermill_job_input_path_is_file(cls, job_dict):
        """
        Papermill input_path must be an existing file.
        """
        assert schema.papermill_job_input_path_is_file(job_dict) is True

    def test_papermill_job_input_path_is_file_not_exists(cls):
        """
        Papermill input_path must be an existing file.
        """
        job_dict = {"input_path": "./test.ipynb"}
        with pytest.raises(InvalidFilePathError):
            schema.papermill_job_input_path_is_file(job_dict)

    def test_papermill_job_paths_ends_with_ipynb_true(cls, job_dict):
        """
        Papermill job paths must point to .ipynb type files.
        """
        assert schema.papermill_job_paths_ends_with_ipynb(job_dict) is True

    @pytest.mark.parametrize(
        "test_input",
        [
            (
                {
                    "name": "job_name",
                    "uses": "papermill",
                    "trigger": "interval",
                    "minutes": 1,
                    "input_path": "./test.txt",
                    "output_path": "./test.ipynb",
                }
            ),
            (
                {
                    "name": "job_name",
                    "uses": "papermill",
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
            schema.papermill_job_paths_ends_with_ipynb(test_input)

    def test_validate_papermill_job_calls_papermill_job_use_has_expected_keys(
        cls, job_dict
    ):
        with unittest.mock.patch(
            "workflower.utils.schema.papermill_job_use_has_expected_keys"
        ) as mock:
            schema.validate_papermill_job(job_dict)
        assert mock.call_count == 1

    def test_validate_papermill_job_calls_papermill_job_input_path_is_file(
        cls, job_dict
    ):
        with unittest.mock.patch(
            "workflower.utils.schema.papermill_job_input_path_is_file"
        ) as mock:
            schema.validate_papermill_job(job_dict)
        assert mock.call_count == 1

    def test_validate_papermill_job_calls_papermill_job_paths_ends_with_ipynb(
        cls, job_dict
    ):
        with unittest.mock.patch(
            "workflower.utils.schema.papermill_job_paths_ends_with_ipynb"
        ) as mock:
            schema.validate_papermill_job(job_dict)
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
            "uses": "alteryx",
            "path": alteryx_workflow_file,
            "trigger": "interval",
            "minutes": 1,
        }

    def test_alteryx_job_use_has_expected_keys(cls, job_dict):
        """
        Job must have expected keys.
        """
        assert schema.alteryx_job_use_has_expected_keys(job_dict) is True
