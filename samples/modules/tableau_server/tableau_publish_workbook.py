import tableauserverclient as TSC
from workflower.modules.module import BaseModule


class Module(BaseModule):
    def __init__(self, plugins=None) -> None:
        self._plugins = plugins

    def run(self, *args, **kwargs):
        # =================================================================== #
        # variables
        # =================================================================== #
        workbook_name = "your_workbook_name"
        project_id = "your_project_id"
        workbook_path = "your_workbook_path"
        # =================================================================== #
        # Plugins
        # =================================================================== #
        tableau_server_plugin = self.get_plugin("tableau_server_plugin")
        # Create a plugin with create_component factory
        server_manager = tableau_server_plugin.create_component(
            "server_manager"
        )
        # =================================================================== #
        # Tableau server client api sigin in
        # =================================================================== #
        server_manager.apply_server_options(dict(verify=False))
        server_manager.sigin_in()
        # =================================================================== #
        # Instance a workbook
        # =================================================================== #
        new_workbook = TSC.WorkbookItem(
            name=workbook_name,
            project_id=project_id,
        )
        # =================================================================== #
        # Publish a workbook
        # =================================================================== #
        server_manager.workbooks.publish(
            new_workbook,
            workbook_path,
            # TSC.Server.PublishMode.CreateNew,
            # TSC.Server.PublishMode.Append,
            TSC.Server.PublishMode.Overwrite,
        )
        # =================================================================== #
        # Tableau server client api sigin out
        # =================================================================== #
        server_manager.sigin_out()
