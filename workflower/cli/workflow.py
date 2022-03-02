import logging
import time

from workflower.adapters.scheduler.setup import (
    create_scheduler,
    create_sqlalchemy_jobstore,
)
from workflower.adapters.sqlalchemy.setup import Session, engine
from workflower.adapters.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from workflower.application.job.commands import ChangeJobStatusCommand
from workflower.config import Config
from workflower.services.workflow.loader import WorkflowLoaderService
from workflower.services.workflow.runner import WorkflowRunnerService

logger = logging.getLogger("workflower.cli.workflow")

jobstores = {
    "default": create_sqlalchemy_jobstore(
        engine=engine, tablename="on_demand_jobs"
    ),
}
executors = {
    "default": {
        "type": "threadpool",
        "max_workers": 20,
    },
}

scheduler = create_scheduler(
    executors=executors, jobstores=jobstores, timezone=Config.TIME_ZONE
)


class Runner:
    """
    Command line workflow runner.
    """

    def run_workflow(self, path) -> None:
        self._is_waiting = True
        session = Session()
        uow = SqlAlchemyUnitOfWork(session)
        workflow_runner = WorkflowRunnerService()
        workflow_loader = WorkflowLoaderService()
        workflow = workflow_loader.load_one_workflow_file(
            path, trigger="on_demand"
        )
        if workflow:
            for job in workflow.jobs:
                change_job_status_command = ChangeJobStatusCommand(
                    uow, job.id, "pending"
                )
                change_job_status_command.execute()
            try:
                workflow_runner.schedule_one_workflow_jobs(
                    uow, workflow, scheduler
                )
            except Exception as error:
                logger.error(f"Error: {error}")
                return
            # Start after a job is scheduled will grantee scheduler is up
            # until job finishess execution
            scheduler.start()
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
