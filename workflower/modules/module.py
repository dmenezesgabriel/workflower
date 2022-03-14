import logging
from abc import ABC, abstractclassmethod


class Module(ABC):
    @abstractclassmethod
    def run(*args, **kwargs):
        pass


class BaseModule(Module):
    def __init__(self, plugins=None) -> None:
        self._plugins = plugins
        self.logger = logging.getLogger(f"workflower.modules.{self.__name__}")

    @property
    def plugins(self):
        return self._plugins

    def get_plugin(self, plugin_name):
        plugins = [
            plugin
            for plugin in self._plugins
            if plugin.__name__ == plugin_name
        ]
        if plugins:
            return plugins[0]

    def run(self, *args, **kwargs):
        pass
