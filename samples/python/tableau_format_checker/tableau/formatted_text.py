from tableau.run import Run


def _run_object_from_run_xml(run_xml):
    return Run.from_run_xml(run_xml)


class FormattedText:
    """
    Layout Options class.
    """

    def __init__(self, runs=None, formatted_text_xml=None) -> None:
        self._runs = runs
        self._formatted_text_xml = formatted_text_xml

        if formatted_text_xml is not None:
            self._initialize_from_formatted_text_xml(self._formatted_text_xml)
            self.runs = self._get_run_objects()

    def _initialize_from_formatted_text_xml(self, xml_data):
        self._run = self._get_run_objects()

    @property
    def run(self):
        return self._run

    @classmethod
    def from_formatted_text_xml(cls, xml_data):
        return cls(formatted_text_xml=xml_data)

    def _get_run_objects(self):
        return [
            _run_object_from_run_xml(xml)
            for xml in self._formatted_text_xml.findall(".//run")
        ]
