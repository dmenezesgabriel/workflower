import pytest
import workflower.utils.schema as schema
from workflower.exceptions import InvalidSchemaError


class TestPipeline:
    def test_pipeline_keys_valid_true(cls):
        """
        Pipeline keys must contain version and workflow.
        """
        dict_obj = {"version": "1.0", "workflow": {}}
        assert schema.pipeline_keys_valid(dict_obj) is True

    @pytest.mark.parametrize(
        "test_input", [({"workflow": {}}), ({"version": "1.0"})]
    )
    def test_pipeline_keys_valid_false(cls, test_input):
        """
        If pipeline keys not contain expected keys should raise Exception.
        """
        with pytest.raises(InvalidSchemaError):
            schema.pipeline_keys_valid(test_input)
