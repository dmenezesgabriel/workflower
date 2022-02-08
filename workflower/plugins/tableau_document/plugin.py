from workflower.plugins.plugin import BasePlugin
from workflower.plugins.tableau_document.formatted_text import FormattedText
from workflower.plugins.tableau_document.layout_options import LayoutOptions
from workflower.plugins.tableau_document.run import Run
from workflower.plugins.tableau_document.title import Title
from workflower.plugins.tableau_document.workbook import Workbook
from workflower.plugins.tableau_document.worksheet import Worksheet


class TableauDocumentPlugin(BasePlugin):
    __name__ = "tableau_document_plugin"
    components = dict(
        workbook=Workbook,
        worksheet=Worksheet,
        layout_options=LayoutOptions,
        title=Title,
        formatted_text=FormattedText,
        run=Run,
    )

    @property
    def name(self):
        return self.name

    def create_component(self, component_name, *args, **kwargs):
        return self.components[component_name](*args, **kwargs)
