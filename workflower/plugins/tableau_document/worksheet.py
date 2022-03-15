from workflower.plugins.tableau_document.layout_options import LayoutOptions


def _layout_options_object_from_xml(layout_options_xml):
    return LayoutOptions.from_layout_options_xml(layout_options_xml)


class Worksheet:
    """
    Worksheet class.
    """

    def __init__(
        self,
        name=None,
        layout_options=None,
        worksheet_xml=None,
    ) -> None:
        self._name = name
        self._layout_options = layout_options
        self._worksheet_xml = worksheet_xml

        if worksheet_xml is not None:
            self._initialize_from_worksheet_xml(self._worksheet_xml)

    @property
    def name(self):
        return self._name

    @property
    def layout_options(self):
        return self._layout_options

    def __repr__(self) -> str:
        return (
            f"<Worksheet(name={self.name}, "
            f"layout_options={self.layout_options})>"
        )

    @classmethod
    def from_worksheet_xml(cls, xml_data):
        return cls(worksheet_xml=xml_data)

    def _initialize_from_worksheet_xml(self, xml_data):
        self._name = xml_data.attrib["name"]
        self._layout_options = self._get_layout_options_object(xml_data)

    def _get_layout_options_object(self, xml_data):
        return _layout_options_object_from_xml(
            self._worksheet_xml.find(".//layout-options")
        )
