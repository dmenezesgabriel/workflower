from workflower.application.plugins.tableau_document.title import Title


def _title_object_from_xml(title_xml):
    return Title.from_title_xml(title_xml)


class LayoutOptions:
    """
    Layout Options class.
    """

    def __init__(self, title=None, layout_options_xml=None) -> None:
        self._title = title
        self._layout_options_xml = layout_options_xml

        if layout_options_xml is not None:
            self._initialize_from_layout_options_xml(self._layout_options_xml)

    def _initialize_from_layout_options_xml(self, xml_data):
        self._title = self._get_title_object(xml_data)

    @property
    def title(self):
        return self._title

    @classmethod
    def from_layout_options_xml(cls, xml_data):
        return cls(layout_options_xml=xml_data)

    def _get_title_object(self, xml_data):
        return _title_object_from_xml(
            self._layout_options_xml.find(".//title")
        )
