from workflower.application.plugins.tableau_document.formatted_text import (
    FormattedText,
)


def _formatted_text_object_from_xml(formatted_text_xml):
    return FormattedText.from_formatted_text_xml(formatted_text_xml)


class Title:
    """
    Title  class.
    """

    def __init__(self, formatted_text=None, title_xml=None) -> None:
        self._formatted_text = formatted_text
        self._title_xml = title_xml

        if title_xml is not None:
            self._initialize_from_title_xml(self._title_xml)

    def _initialize_from_title_xml(self, xml_data):
        self._formatted_text = self._get_formatted_text_object(xml_data)

    @property
    def formatted_text(self):
        return self._formatted_text

    @classmethod
    def from_title_xml(cls, xml_data):
        return cls(title_xml=xml_data)

    def _get_formatted_text_object(self, xml_data):
        return _formatted_text_object_from_xml(
            self._title_xml.find(".//formatted-text")
        )
