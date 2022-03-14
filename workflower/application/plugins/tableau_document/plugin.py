from workflower.application.plugins.plugin import BasePlugin
from workflower.application.plugins.tableau_document.formatted_text import (
    FormattedText,
)
from workflower.application.plugins.tableau_document.layout_options import (
    LayoutOptions,
)
from workflower.application.plugins.tableau_document.run import Run
from workflower.application.plugins.tableau_document.title import Title
from workflower.application.plugins.tableau_document.workbook import Workbook
from workflower.application.plugins.tableau_document.worksheet import Worksheet


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
