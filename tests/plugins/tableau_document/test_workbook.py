import xml.etree.ElementTree as et

import pytest
from workflower.plugins.tableau_document.workbook import Workbook
from workflower.plugins.tableau_document.worksheet import Worksheet


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

        # Xml parser
        tree = et.parse(workbook_path)
        tree.getroot()

        #  Workbook instance
        workbook = Workbook(workbook_path)

        assert isinstance(workbook, Workbook)
        assert workbook.name == "sample"
        assert len(workbook.worksheets) == len(tree.findall(".//worksheet"))
        assert all(
            isinstance(worksheet, Worksheet)
            for worksheet in workbook.worksheets
        )
