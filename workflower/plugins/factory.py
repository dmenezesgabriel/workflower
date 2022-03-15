from workflower.plugins.tableau_document.plugin import (
    TableauDocumentPlugin,
)
from workflower.plugins.tableau_server.plugin import (
    TableauServerPlugin,
)


def create_plugin(name: str):
    """
    Plugin Factory.
    """
    plugins = {
        "tableau_document_plugin": TableauDocumentPlugin(),
        "tableau_server_plugin": TableauServerPlugin(),
    }
    return plugins[name]
