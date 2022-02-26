import logging
import os
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from workflower.adapters.scheduler.scheduler import WorkflowScheduler
from workflower.adapters.sqlalchemy.setup import metadata
from workflower.adapters.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from workflower.application.workflow.commands import (
    LoadWorkflowFromYamlFileCommand,
)
from workflower.config import Config

# from workflower.models.base import database
from workflower.services.workflow.runner import WorkflowRunnerService

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
        self._is_waiting = False

    def _setup(self) -> None:
        metadata.drop_all(bind=self.engine)
        metadata.create_all(bind=self.engine)

    def _session(self):
        return scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
            )
        )

    def run_workflow(self, path) -> None:
        self._setup()
        self._is_waiting = True
        session = self._session()
        uow = SqlAlchemyUnitOfWork(session)
        workflow_scheduler = WorkflowScheduler(self.engine)
        workflow_runner = WorkflowRunnerService(self.engine)
        command = LoadWorkflowFromYamlFileCommand(uow, path)
        workflow = command.execute()
        try:
            workflow_runner.schedule_one_workflow_jobs(
                uow, workflow, workflow_scheduler.scheduler
            )
        except Exception as error:
            logger.error(f"Error: {error}")
            return
        # Start after a job is scheduled will grantee scheduler is up
        # until job finishess execution
        workflow_scheduler.start()
        while self._is_waiting:
            with uow:
                workflow_record = uow.workflows.get(id=workflow.id)
                not_pending = all(
                    job.status != "pending" for job in workflow_record.jobs
                )
                # check
                logger.debug([job.status for job in workflow_record.jobs])
                time.sleep(2)
                if not_pending:
                    self._is_waiting = False


def run_workflow(path: str) -> None:
    """
    Run a single workflow by its path.
    """
    runner = Runner()
    runner.run_workflow(path)
