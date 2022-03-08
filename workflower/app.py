from workflower.config import ConfigurationFactory
from workflower.utils.variables import get_env


# WIP
class Workflower:
    def __init__(self, instance_config_environment: bool = False):
        self.config = self.make_config(instance_config_environment)

    def make_config(self, instance_config_environment):
        if not instance_config_environment:
            workflower_env = get_env()
        return ConfigurationFactory.get_config(workflower_env)
