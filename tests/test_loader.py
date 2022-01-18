import pytest
import workflower.utils.schema as schema
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
    assert schema.validate_schema(configuration_dict) is True


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
        schema.validate_schema(configuration_dict)


def test_validate_invalid_version_type():
    with pytest.raises(InvalidTypeError):
        yaml_config = """
        version: 1
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
        schema.validate_schema(configuration_dict)


def test_validate_invalid_workflow_name_type():
    with pytest.raises(InvalidTypeError):
        yaml_config = """
        version: "1.0"
        workflow:
          name: 123
          jobs:
            - name: "papermill_sample"
              uses: papermill
              input_path: ""
              output_path: ""
              trigger: cron
              minute: "*/5"
        """
        configuration_dict = yaml.safe_load(yaml_config)
        schema.validate_schema(configuration_dict)


def test_validate_missing_workflow():
    with pytest.raises(InvalidSchemaError):
        yaml_config = """
        version: "1.0"
        """
        configuration_dict = yaml.safe_load(yaml_config)
        schema.validate_schema(configuration_dict)


def test_validate_missing_jobs():
    with pytest.raises(InvalidSchemaError):
        yaml_config = """
        version: "1.0"
        workflow:
          name: papermill_sample_date_trigger
        """
        configuration_dict = yaml.safe_load(yaml_config)
        schema.validate_schema(configuration_dict)


def test_validate_job_has_name():
    with pytest.raises(InvalidSchemaError):
        yaml_config = """
        version: "1.0"
        workflow:
          name: papermill_sample_date_trigger
          jobs:
            - uses: papermill
              input_path: ""
              output_path: ""
              trigger: cron
              minute: "*/5"
        """
        configuration_dict = yaml.safe_load(yaml_config)
        schema.validate_schema(configuration_dict)


def test_validate_job_has_uses():
    with pytest.raises(InvalidSchemaError):
        yaml_config = """
        version: "1.0"
        workflow:
          name: papermill_sample_date_trigger
          jobs:
            - name: "papermill_sample"
              input_path: ""
              output_path: ""
              trigger: cron
              minute: "*/5"
        """
        configuration_dict = yaml.safe_load(yaml_config)
        schema.validate_schema(configuration_dict)


def test_validate_invalid_uses():
    with pytest.raises(InvalidSchemaError):
        yaml_config = """
        version: "1.0"
        workflow:
          name: papermill_sample_date_trigger
          jobs:
            - name: "papermill_sample"
              uses: something
              input_path: ""
              output_path: ""
              trigger: cron
              minute: "*/5"
        """
        configuration_dict = yaml.safe_load(yaml_config)
        schema.validate_schema(configuration_dict)


def test_validate_uses_alteryx():
    yaml_config = """
    version: "1.0"
    workflow:
      name: papermill_sample_date_trigger
      jobs:
        - name: "papermill_sample"
          uses: alteryx
          path: ""
          trigger: cron
          minute: "*/5"
    """
    configuration_dict = yaml.safe_load(yaml_config)
    assert schema.validate_schema(configuration_dict) is True


def test_validate_uses_papermill():
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
    assert schema.validate_schema(configuration_dict) is True


def test_validate_job_has_trigger():
    with pytest.raises(InvalidSchemaError):
        yaml_config = """
        version: "1.0"
        workflow:
          name: papermill_sample_date_trigger
          jobs:
            - name: "papermill_sample"
              uses: papermill
              input_path: ""
              output_path: ""
        """
        configuration_dict = yaml.safe_load(yaml_config)
        schema.validate_schema(configuration_dict)


def test_validate_invalid_trigger():
    with pytest.raises(InvalidSchemaError):
        yaml_config = """
        version: "1.0"
        workflow:
          name: papermill_sample_date_trigger
          jobs:
            - name: "papermill_sample"
              uses: papermill
              input_path: ""
              output_path: ""
              trigger: something
              minute: "*/5"
        """
        configuration_dict = yaml.safe_load(yaml_config)
        schema.validate_schema(configuration_dict)


def test_validate_trigger_date():
    yaml_config = """
    version: "1.0"
    workflow:
      name: papermill_sample_date_trigger
      jobs:
        - name: "papermill_sample"
          uses: papermill
          input_path: ""
          output_path: ""
          trigger: date
    """
    configuration_dict = yaml.safe_load(yaml_config)
    assert schema.validate_schema(configuration_dict) is True


def test_validate_trigger_cron():
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
    """
    configuration_dict = yaml.safe_load(yaml_config)
    assert schema.validate_schema(configuration_dict) is True


def test_validate_trigger_interval():
    yaml_config = """
    version: "1.0"
    workflow:
      name: papermill_sample_date_trigger
      jobs:
        - name: "papermill_sample"
          uses: papermill
          input_path: ""
          output_path: ""
          trigger: interval
    """
    configuration_dict = yaml.safe_load(yaml_config)
    assert schema.validate_schema(configuration_dict) is True
