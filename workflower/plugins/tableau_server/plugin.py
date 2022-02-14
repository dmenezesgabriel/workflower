from workflower.plugins.plugin import BasePlugin
from workflower.plugins.tableau_server.server import ServerManager


class TableauServerPlugin(BasePlugin):
    __name__ = "tableau_server_plugin"
    components = dict(
        server_manager=ServerManager,
    )
