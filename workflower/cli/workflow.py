import logging
import os
import time

from workflower.config import Config
from workflower.controllers.workflow import WorkflowContoller
from workflower.database import DatabaseManager
from workflower.init_db import init_db

# from workflower.models.base import database
from workflower.models import Workflow
from workflower.models.base import BaseModel
from workflower.scheduler import SchedulerService

logger = logging.getLogger("workflower.cli.workflow")
database_file = os.path.join(Config.DATA_DIR, "temp.sqlite")
database_uri = f"sqlite:///{database_file}"


class Runner:
    # TODO
    # must improve this

    def __init__(self, database_uri=database_uri) -> None:
        self._database_uri = database_uri
        self._database = None
        self._is_running = False

    def _setup(self):
        self._database = DatabaseManager(self._database_uri)
        #  Clean db
        BaseModel.metadata.drop_all(bind=self._database.engine)
        #  Init database
        init_db(self._database)

    def run_workflow(self, path):
        self._setup()
        self._is_running = True
        with self._database.session_scope() as session:
            scheduler_service = SchedulerService(self._database)
            workflow_controller = WorkflowContoller(self._database)
            workflow = Workflow.from_yaml(session, path)
            workflow_controller.schedule_one_workflow_jobs(
                session, workflow, scheduler_service.scheduler
            )
            # Start after a job is scheduled will grantee scheduler is up
            # until job finishess execution
            scheduler_service.start()
            # After job is executed if we don 't wait till the next jobs is
            # added to scheduler by the execution event, scheduler will be
            # shutted down
            # wait till trigger deps
            time.sleep(1)
        self._is_running = False


def run_workflow(path):
    runner = Runner()
    return runner.run_workflow(path)
