import pytest
import workflower.loader as loader
import yaml
from workflower.exceptions import InvalidSchemaError, InvalidTypeError


def test_validate_true():
    yaml_config = """
    version: "1.0"
    workflow:
      name: papermill_sample_date_trigger
      jobs:
        - name: "papermill_sample"
          uses: papermill
          input_path: ""
          output_path: ""
          trigger: cron
          minute: "*/5"
    """
    configuration_dict = yaml.safe_load(yaml_config)
    assert loader.validate_schema(configuration_dict) is True


def test_validate_missing_version():
    with pytest.raises(InvalidSchemaError):
        yaml_config = """
        workflow:
          name: papermill_sample_date_trigger
          jobs:
            - name: "papermill_sample"
              uses: papermill
              input_path: ""
              output_path: ""
              trigger: cron
              minute: "*/5"
        """
        configuration_dict = yaml.safe_load(yaml_config)
        loader.validate_schema(configuration_dict)


def test_validate_missing_workflow():
    with pytest.raises(InvalidSchemaError):
        yaml_config = """
        version: "1.0"
        """
        configuration_dict = yaml.safe_load(yaml_config)
        loader.validate_schema(configuration_dict)


def test_validate_missing_jobs():
    with pytest.raises(InvalidSchemaError):
        yaml_config = """
        version: "1.0"
        workflow:
          name: papermill_sample_date_trigger
        """
        configuration_dict = yaml.safe_load(yaml_config)
        loader.validate_schema(configuration_dict)
