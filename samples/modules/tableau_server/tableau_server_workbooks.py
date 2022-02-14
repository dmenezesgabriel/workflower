import tableauserverclient as TSC
from workflower.modules.module import BaseModule


class Module(BaseModule):
    def __init__(self, plugins=None) -> None:
        self._plugins = plugins

    def run(self, *args, **kwargs):
        tableau_server_plugin = self.get_plugin("tableau_server_plugin")
        server_manager = tableau_server_plugin.create_component(
            "server_manager"
        )
        server_manager.apply_server_options(dict(verify=False))
        server_manager.sigin_in()
        all_workbooks = TSC.Pager(server_manager.server.workbooks)
        for workbook in all_workbooks:
            print(40 * "=")
            print(f"Workbook{workbook.name}")
            print(40 * "=")
