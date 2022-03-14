import pytest
from workflower.application.plugins.tableau_document.workbook import Workbook


class TestWorkbookInstance:
    @pytest.fixture
    def workbook_file(self, tmpdir_factory):
        with open("tests/resources/sample.twb") as f:
            file_content = f.read()
        p = tmpdir_factory.mktemp("file").join("sample.twb")
        p.write_text(file_content, encoding="utf-8")
        return p

    def test_Workbook_initialize_correctly(self, workbook_file):
        workbook_path = str(workbook_file)
        workbook = Workbook(workbook_path)

        assert isinstance(workbook, Workbook)
        assert workbook.name == "sample"
