_ATTRIBUTES = [
    "bold",
    "underline",
    "fontname",
    "fontsize",
    "fontcolor",
    "fontalignment",
]


class Run:
    """
    Layout Options class.
    """

    def __init__(self, content=None, run_xml=None) -> None:
        self.content = content
        self._run_xml = run_xml

        # Initialize all the possible attributes
        for attrib in _ATTRIBUTES:
            setattr(self, f"_{attrib}", None)

        if run_xml is not None:
            self._initialize_from_run_xml(run_xml)
            self.content = run_xml.text

    @property
    def bold(self):
        return self._bold

    @property
    def underline(self):
        return self._underline

    @property
    def fontname(self):
        return self._fontname

    @property
    def fontsize(self):
        return self._fontsize

    @property
    def fontcolor(self):
        return self._fontcolor

    @property
    def fontalignment(self):
        return self._fontalignment

    def _initialize_from_run_xml(self, xml_data):
        for attrib in _ATTRIBUTES:
            self._apply_attribute(
                xml_data, attrib, lambda x: xml_data.attrib.get(x, None)
            )

    @classmethod
    def from_run_xml(cls, xml_data):
        return cls(run_xml=xml_data)

    def _apply_attribute(self, xml_data, attrib, default_func, read_name=None):
        if read_name is None:
            read_name = attrib
        if hasattr(self, f"_read_{read_name}"):
            value = getattr(self, f"_read_{read_name}")(xml_data)
        else:
            value = default_func(attrib)

        setattr(self, f"_{attrib}", value)
