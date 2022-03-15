from workflower.plugins.tableau_document.formatted_text import FormattedText


def _formatted_text_object_from_xml(formatted_text_xml):
    return FormattedText.from_formatted_text_xml(formatted_text_xml)


_ATTRIBUTES = [
    "id",
    "name",
    "h",
    "w",
    "x",
    "y",
    "mode",
    "values",
]


class Zone:
    """
    Zone class.
    """

    def __init__(self, zone_xml=None) -> None:
        # Initialize all the possible attributes
        for attrib in _ATTRIBUTES:
            setattr(self, f"_{attrib}", None)

        if zone_xml is not None:
            self._initialize_from_zone_xml(zone_xml)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def friendly_name(self):
        return self._friendly_name

    @property
    def type(self):
        return self._type

    @property
    def show_apply(self):
        return self._show_apply

    @property
    def mode(self):
        return self._mode

    @property
    def values(self):
        return self._values

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def height(self):
        return self._h

    @property
    def width(self):
        return self._w

    @property
    def formatted_text(self):
        return self._formatted_text

    def __repr__(self) -> str:
        return (
            f"<Zone(name={self.name}, "
            f"id={self.id}, "
            f"friendly_name={self.friendly_name}, "
            f"type={self.type}, "
            f"show_apply={self.show_apply}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"height={self.height}, "
            f"width={self.width}, "
            f"_formatted_text={self._formatted_text}"
            ")>"
        )

    @classmethod
    def from_zone_xml(cls, xml_data):
        return cls(zone_xml=xml_data)

    def _apply_attribute(self, xml_data, attrib, default_func, read_name=None):
        if read_name is None:
            read_name = attrib
        if hasattr(self, f"_read_{read_name}"):
            value = getattr(self, f"_read_{read_name}")(xml_data)
        else:
            value = default_func(attrib)

        setattr(self, f"_{attrib}", value)

    def _initialize_from_zone_xml(self, xml_data):
        # TODO
        # Improve this
        self._friendly_name = xml_data.get("friendly-name", None)
        self._type = xml_data.get("type-v2", None)
        self._show_apply = xml_data.get("show-apply", None)

        for attrib in _ATTRIBUTES:
            self._apply_attribute(
                xml_data, attrib, lambda x: xml_data.attrib.get(x, None)
            )

        self._formatted_text = self._get_formatted_text_object(xml_data)

    def _get_formatted_text_object(self, xml_data):
        return _formatted_text_object_from_xml(
            xml_data.find(".//formatted-text")
        )
