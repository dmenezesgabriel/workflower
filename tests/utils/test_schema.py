import pytest
import workflower.utils.schema as schema
from workflower.exceptions import InvalidSchemaError, InvalidTypeError


class TestPipeline:
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
        If pipeline keys not contain expected keys should raise Exception.
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


class TestWorkflow:
    def test_workflow_value_is_dict_type_true(cls):
        """
        Workflow must be dict type.
        """
        dict_obj = {"version": "1.0", "workflow": {}}
        assert schema.workflow_value_is_dict_type(dict_obj) is True

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

    def test_workflow_has_expected_keys(cls):
        """
        Workflow must have expected keys.
        """
        dict_obj = {"workflow": {"name": "workflow_name", "jobs": []}}
        assert schema.workflow_has_expected_keys(dict_obj) is True
