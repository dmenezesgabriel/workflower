import os.path
import time
import unittest.mock

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

    def mock_os_path_basename(self, monkeypatch):
        """
        Mock os.path.basename.
        """
        return "test_file.yaml"

    def mock_os_path_splittext(cls, monkeypatch):
        """
        mock os.path.splitext.
        """
        return ["test_file", ".yaml"]

    def test_get_file_name_calls_os_path_basename(cls, temp_workflow_file):
        """
        os.path.basename should be called once.
        """
        with unittest.mock.patch("os.path.basename") as mock_basename:
            get_file_name(temp_workflow_file)
            mock_basename.assert_called_once()

    def test_get_file_name_calls_os_path_splittext(cls, temp_workflow_file):
        """
        os.path.splitext should be called once.
        """
        with unittest.mock.patch("os.path.splitext") as mock_splittext:
            get_file_name(temp_workflow_file)
            mock_splittext.assert_called_once()

    def test_get_file_name_return(cls, temp_workflow_file, monkeypatch):
        """
        Return value must be a file name without extension.
        """
        monkeypatch.setattr(os.path, "basename", cls.mock_os_path_basename)
        monkeypatch.setattr(os.path, "splitext", cls.mock_os_path_splittext)
        assert get_file_name(temp_workflow_file) == "test_file"

    def test_get_file_name_return_type(cls, temp_workflow_file, monkeypatch):
        """
        Return must be string type.
        """
        monkeypatch.setattr(os.path, "basename", cls.mock_os_path_basename)
        monkeypatch.setattr(os.path, "splitext", cls.mock_os_path_splittext)
        assert isinstance(get_file_name(temp_workflow_file), str)


class TestGetFileModificationDate:
    """
    Test case for get_file_modification_date function.
    """

    def mock_os_path_getmtime(cls, monkeypatch):
        """
        Mock os.path.getmtime.
        """
        return time.time()

    def test_get_file_modification_date_calls_os_path_basename(
        cls, temp_workflow_file
    ):
        """
        os.path.getmtime should be called once.
        """
        with unittest.mock.patch("os.path.getmtime") as mock_getmtime:
            get_file_modification_date(temp_workflow_file)
            mock_getmtime.assert_called_once()

    def test_get_file_modification_date_return_type(
        cls, temp_workflow_file, monkeypatch
    ):
        """
        Return type must be a floating point representing seconds between
        epoch and file's modification time.
        """
        monkeypatch.setattr(os.path, "getmtime", cls.mock_os_path_getmtime)
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

    def mock_yaml_safe_load(cls, monkeypatch):
        """
        Mock yaml.safe_load.
        """
        return {
            "version": "1.0",
            "workflow": None,
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
        }

    def test_yaml_file_to_dict_calls_yaml_safe_load(cls, temp_workflow_file):
        """
        os.path.basename should be called once.
        """
        with unittest.mock.patch("yaml.safe_load") as mock_safe_load:
            yaml_file_to_dict(temp_workflow_file)
            mock_safe_load.assert_called_once()

    def test_yaml_file_to_dict(cls, temp_workflow_file, monkeypatch):
        """
        Valid yaml file from path must return a dict.
        """
        yaml_dict = yaml_file_to_dict(temp_workflow_file)
        monkeypatch.setattr(yaml, "safe_load", cls.test_yaml_file_to_dict)
        mock_open = unittest.mock.mock_open(read_data=cls.read_data)
        with unittest.mock.patch("builtins.open", mock_open):
            assert isinstance(yaml_dict, dict)
