from abc import ABC, abstractclassmethod


class BasePlugin(ABC):
    """
    Plugin Base class.
    """

    name = __name__
    components = None

    @property
    @abstractclassmethod
    def name(self):
        pass

    @abstractclassmethod
    def create_component(self, component_name, *args, **kwargs):
        pass
