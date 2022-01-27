import os.path
import time
import unittest.mock
from unittest.mock import MagicMock

import pytest
import yaml
from workflower.utils.file import (
    get_file_modification_date,
    get_file_name,
    yaml_file_to_dict,
)


@pytest.fixture(scope="function")
def temp_workflow_file(tmpdir_factory):
    file_content = """
    version: "1.0"
    workflow:
    name: python_code_sample_interval_trigger
    jobs:
      - name: "hello_python_code"
        uses: python
        code: "print('Hello, World!')"
        trigger: interval
        minutes: 2
    """
    p = tmpdir_factory.mktemp("file").join("test_file.yaml")
    p.write_text(file_content, encoding="utf-8")
    return str(p)


class TestGetFileName:
    """
    Test case for get_file_name function.
    """

    def test_get_file_name_calls_os_path_basename(cls, temp_workflow_file):
        """
        os.path.basename should be called once.
        """
        with unittest.mock.patch("os.path.basename") as mock:
            get_file_name(temp_workflow_file)
            assert mock.call_count == 1

    def test_get_file_name_calls_os_path_splitext(cls, temp_workflow_file):
        """
        os.path.splitext should be called once.
        """
        with unittest.mock.patch("os.path.splitext") as mock:
            get_file_name(temp_workflow_file)
            assert mock.call_count == 1

    def test_get_file_name_return(cls, temp_workflow_file):
        """
        Return value must be a file name without extension.
        """
        os.path.basename = MagicMock(return_value="test_file.yaml")
        os.path.splitext = MagicMock(return_value=["test_file", ".yaml"])
        assert get_file_name(temp_workflow_file) == "test_file"

    def test_get_file_name_return_type(cls, temp_workflow_file):
        """
        Return must be string type.
        """
        os.path.basename = MagicMock(return_value="test_file.yaml")
        os.path.splitext = MagicMock(return_value=["test_file", ".yaml"])
        assert isinstance(get_file_name(temp_workflow_file), str)


class TestGetFileModificationDate:
    """
    Test case for get_file_modification_date function.
    """

    def test_get_file_modification_date_calls_os_path_basename(
        cls, temp_workflow_file
    ):
        """
        os.path.getmtime should be called once.
        """
        with unittest.mock.patch("os.path.getmtime") as mock:
            get_file_modification_date(temp_workflow_file)
            assert mock.call_count == 1

    def test_get_file_modification_date_return_type(cls, temp_workflow_file):
        """
        Return type must be a floating point representing seconds between
        epoch and file's modification time.
        """

        os.path.getmtime = MagicMock(return_value=time.time())
        file_modification_date = get_file_modification_date(temp_workflow_file)
        assert isinstance(file_modification_date, float)


class TestYamlFileToDict:
    """
    Test case for yaml_file_to_dict function.
    """

    read_data = """
            version: "1.0"
            workflow:
              name: python_code_sample_interval_trigger
              jobs:
                - name: "hello_python_code"
                  uses: python
                  code: "print('Hello, World!')"
                  trigger: interval
                  minutes: 2
        """

    mock_open = unittest.mock.mock_open(read_data=read_data)

    mock_dict = {
        "version": "1.0",
        "workflow": {
            "name": "python_code_sample_interval_trigger",
            "jobs": [
                {
                    "name": "hello_python_code",
                    "uses": "python",
                    "code": "print('Hello, World!')",
                    "trigger": "interval",
                    "minutes": 2,
                }
            ],
        },
    }

    def test_yaml_file_to_dict_calls_yaml_safe_load(cls, temp_workflow_file):
        """
        os.path.basename should be called once.
        """
        with unittest.mock.patch("builtins.open", cls.mock_open):
            with unittest.mock.patch("yaml.safe_load") as mock:
                yaml_file_to_dict(temp_workflow_file)
                assert mock.call_count == 1

    def test_yaml_file_to_dict(cls, temp_workflow_file):
        """
        Valid yaml file from path must return a dict.
        """
        yaml.safe_load = MagicMock(return_value=cls.mock_dict)
        with unittest.mock.patch("builtins.open", cls.mock_open):
            yaml_dict = yaml_file_to_dict(temp_workflow_file)
            assert isinstance(yaml_dict, dict)
