from workflower.plugins.tableau_document.size import Size
from workflower.plugins.tableau_document.zone import Zone


def _zone_object_from_zone_xml(dashboard_xml):
    return Zone.from_zone_xml(dashboard_xml)


def _size_object_from_xml(size_xml):
    return Size.from_size_xml(size_xml)


class Dashboard:
    """
    Dashboard class.
    """

    def __init__(
        self,
        name=None,
        zones=None,
        dashboard_xml=None,
    ) -> None:
        self._name = name
        self._zones = zones
        self._dashboard_xml = dashboard_xml

        if dashboard_xml is not None:
            self._initialize_from_dashboard_xml(self._dashboard_xml)

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def zones(self):
        return self._zones

    def __repr__(self) -> str:
        return (
            "<Dashboard("
            f"name={self.name}, "
            f"size={self.size}, "
            f"zones={self.zones}"
            ")>"
        )

    @classmethod
    def from_dashboard_xml(cls, xml_data):
        return cls(dashboard_xml=xml_data)

    def _initialize_from_dashboard_xml(self, xml_data):
        self._name = xml_data.get("name", None)
        self._zones = self._get_zones_objects()
        self._size = self._get_size_object(xml_data)

    def _get_zones_objects(self):
        return [
            _zone_object_from_zone_xml(xml)
            for xml in self._dashboard_xml.findall(".//zone")
        ]

    def _get_size_object(self, xml_data):
        return _size_object_from_xml(xml_data.find(".//size"))
