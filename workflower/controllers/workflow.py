import asyncio
import logging
import os

from workflower.config import Config
from workflower.database import DatabaseManager
from workflower.loader import WorkflowLoader
from workflower.models.base import database
from workflower.models.workflow import Workflow
from workflower.utils import crud

logger = logging.getLogger("workflower.controllers.workflow")


class WorkflowContoller:
    """
    Workflow Controller.
    """

    def __init__(self, engine) -> None:
        self.workflow_loader = WorkflowLoader()
        self.is_running = False
        self.engine = engine
        self._init()

    def create_default_directories(self) -> None:
        """
        Create application default configuration directories.
        """
        if not os.path.isdir(Config.ENVIRONMENTS_DIR):
            os.makedirs(Config.ENVIRONMENTS_DIR)

        if not os.path.isdir(Config.DATA_DIR):
            os.makedirs(Config.DATA_DIR)

    def _init(self) -> None:
        """
        Workflow Controller Initial Setup.
        """
        self.create_default_directories()

    def schedule_one_workflow_jobs(
        self, session, workflow: Workflow, scheduler
    ) -> None:
        """
        Schedule one workflow
        """
        logger.info(f"Trying to schedule {workflow.name}")
        if workflow.file_exists:
            if workflow.modified_since_last_load:
                logger.info(
                    f"{workflow.name} file has been modified, "
                    "unscheduling jobs"
                )
                workflow.unschedule_jobs(scheduler)
        elif not workflow.file_exists:
            logger.info(
                f"{workflow.name} file has been removed, unscheduling jobs"
            )
            crud.update(
                session,
                Workflow,
                dict(id=workflow.id),
                dict(is_active=False),
            )
            workflow.deactivate_all_jobs(session)
            workflow.unschedule_jobs(scheduler)
            logger.info(f"{workflow.name} file removed, skipping")
            return
        logger.info("Scheduling jobs")
        workflow.schedule_jobs(session, scheduler)

    def schedule_workflows_jobs(self, scheduler) -> None:
        """
        run Workflow Controller.
        """
        logger.info("Scheduling workflows jobs")
        with self._database.session_scope() as session:
            # Load all workflows into database, it won't load if file has been
            # removed.
            self.workflow_loader.load_all_from_dir(session)
            # Load all workflows on database, including if the file has ben
            # removed.
            workflows = crud.get_all(session, Workflow)
            for workflow in workflows:
                self.update_workflow_files_exists_state(session, workflow)
                self.schedule_one_workflow_jobs(session, workflow, scheduler)

    async def run(self, scheduler):
        self.is_running = True
        while self.is_running:
            self.schedule_workflows_jobs(scheduler)
            logger.info(f"Sleeping {Config.CYCLE} seconds")
            await asyncio.sleep(Config.CYCLE)

    def stop(self):
        self.is_running = False
