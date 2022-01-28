import unittest
import unittest.mock

import pytest
import workflower.utils.schema as schema
from workflower.exceptions import InvalidSchemaError, InvalidTypeError


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
        Workflow must have expected keys.
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
        If Workflow not contain expected keys should raise Exception.
        """
        with pytest.raises(InvalidSchemaError):
            schema.job_has_expected_keys(test_input)

    def test_job_name_is_string_type_true(cls, job_dict):
        """
        Workflow must be dict type.
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
