import time

from workflower.adapters.sqlalchemy.backup import backup_sqlite
from workflower.config import Config
from workflower.modules.module import BaseModule


class Module(BaseModule):
    def __init__(self, plugins=None) -> None:
        self._plugins = plugins

    def run(self, *args, **kwargs):
        start_time = time.time()
        backup_sqlite(Config.APP_DATABASE_URL, Config.APP_DATABASE_BACKUP_URL)
        end_time = time.time()
        elapsed_time = end_time - start_time
        return f"elapsed time: {elapsed_time} seconds"
