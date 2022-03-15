_ATTRIBUTES = [
    "maxheight",
    "maxwidth",
    "minheight",
    "minwidth",
]


class Size:
    """
    Layout Options class.
    """

    def __init__(self, content=None, size_xml=None) -> None:
        self.content = content
        self._size_xml = size_xml

        # Initialize all the possible attributes
        for attrib in _ATTRIBUTES:
            setattr(self, f"_{attrib}", None)

        if size_xml is not None:
            self._initialize_from_size_xml(size_xml)
            self.content = size_xml.text

    @property
    def maxheight(self):
        return self._maxheight

    @property
    def maxwidth(self):
        return self._maxwidth

    @property
    def minheight(self):
        return self._minheight

    @property
    def minwidth(self):
        return self._minwidth

    def _initialize_from_size_xml(self, xml_data):
        for attrib in _ATTRIBUTES:
            self._apply_attribute(
                xml_data, attrib, lambda x: xml_data.attrib.get(x, None)
            )

    def __repr__(self) -> str:
        return (
            "<Size("
            f"maxheight={self.maxheight}, "
            f"maxwidth={self.maxwidth}, "
            f"minheight={self.minheight}, "
            f"minwidth={self.minwidth}, "
            ")>"
        )

    @classmethod
    def from_size_xml(cls, xml_data):
        return cls(size_xml=xml_data)

    def _apply_attribute(self, xml_data, attrib, default_func, read_name=None):
        if read_name is None:
            read_name = attrib
        if hasattr(self, f"_read_{read_name}"):
            value = getattr(self, f"_read_{read_name}")(xml_data)
        else:
            value = default_func(attrib)

        setattr(self, f"_{attrib}", value)
