import logging
import os
import time

from sqlalchemy import create_engine
from workflower.config import Config
from workflower.controllers.workflow import WorkflowContoller

# from workflower.models.base import database
from workflower.models import Workflow
from workflower.models.base import BaseModel
from workflower.scheduler import SchedulerService

logger = logging.getLogger("workflower.cli.workflow")
# Must improve this
database_file = os.path.join(Config.DATA_DIR, "temp.sqlite")
database_uri = f"sqlite:///{database_file}"


class Runner:
    """
    Command line workflow runner.
    """

    def __init__(self) -> None:
        self.engine = create_engine(database_uri)
        self._is_running = False

    def _setup(self) -> None:
        #  Clean db
        BaseModel.metadata.drop_all(bind=self.engine)
        #  Init database

    def run_workflow(self, path) -> None:
        self._setup()
        self._is_running = True
        with self._database.session_scope() as session:
            scheduler_service = SchedulerService(self.engine)
            workflow_controller = WorkflowContoller(self.engine)
            workflow = Workflow.from_yaml(session, path)
            workflow_controller.schedule_one_workflow_jobs(
                session, workflow, scheduler_service.scheduler
            )
            # Start after a job is scheduled will grantee scheduler is up
            # until job finishess execution
            scheduler_service.start()
            # TODO
            # =============================================================== #
            # As is
            # After job is executed if we don 't wait till the next jobs is
            # added to scheduler by the execution event, scheduler will be
            # shutted down
            # wait till trigger deps
            time.sleep(10)
            # To be
            # Know which jobs must be executed
            # Keep scheduler service running until last job finished
            # =============================================================== #
        self._is_running = False


def run_workflow(path: str) -> None:
    """
    Run a single workflow by its path.
    """
    runner = Runner()
    runner.run_workflow(path)
