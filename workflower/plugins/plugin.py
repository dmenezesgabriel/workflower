from abc import ABC, abstractclassmethod


class PluginInterface(ABC):
    """
    Plugin interface.
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


class BasePlugin(PluginInterface):
    """
    Base Plugin.
    """

    name = __name__
    components = None

    @property
    def name(self):
        return self.name

    def create_component(self, component_name, *args, **kwargs):
        return self.components[component_name](*args, **kwargs)
