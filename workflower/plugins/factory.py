from workflower.plugins.tableau_document.plugin import TableauDocumentPlugin


def create_plugin(name: str):
    """
    Plugin Factory.
    """
    plugins = {"tableau_document": TableauDocumentPlugin()}
    return plugins[name]
