import pytest
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
    def test_get_file_name_return(self, temp_workflow_file):
        assert get_file_name(temp_workflow_file) == "test_file"

    def test_get_file_name_return_type(self, temp_workflow_file):
        assert isinstance(get_file_name(temp_workflow_file), str)


class TestGetFileModificationDate:
    def test_get_file_modification_date_return_type(self, temp_workflow_file):
        file_modification_date = get_file_modification_date(temp_workflow_file)
        assert isinstance(file_modification_date, float)


class TestYamlFileToDict:
    def test_yaml_file_to_dict(self, temp_workflow_file):
        assert isinstance(yaml_file_to_dict(temp_workflow_file), dict)
