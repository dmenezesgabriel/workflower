import os
import xml.etree.ElementTree as et

from workflower.plugins.tableau_document.worksheet import Worksheet


def _worksheet_object_from_worksheet_xml(worksheet_xml):
    return Worksheet.from_worksheet_xml(worksheet_xml)


class Workbook:
    """
    Workbook class.
    """

    def __init__(self, file_name) -> None:
        self._file_name = file_name
        self._name = os.path.splitext(os.path.basename(self._file_name))[0]
        self._workbook_tree = et.parse(self._file_name)
        self._workbook_root = self._workbook_tree.getroot()
        self._worksheets = self._get_worksheets_objects()

    @property
    def name(self):
        return self._name

    @property
    def worksheets(self):
        return self._worksheets

    def __repr__(self) -> str:
        return f"<Workbook(name={self.name})>"

    def _get_worksheets_objects(self):
        return [
            _worksheet_object_from_worksheet_xml(xml)
            for xml in self._workbook_tree.findall(".//worksheet")
        ]
