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

    def __init__(self, database: DatabaseManager = database) -> None:
        self.workflow_loader = WorkflowLoader()
        self.is_running = False
        self._database = database
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

    def update_workflow_files_exists_state(self, session, workflow) -> None:
        """
        Check if file exists and update state.
        """
        file_exists = os.path.isfile(workflow.file_path)
        if file_exists:
            logger.debug(f"{workflow.name} file exists")
            update_dict = {"file_exists": True}
        else:
            logger.info(f"{workflow.name} file not exists")
            update_dict = {"file_exists": False}
        filter_dict = {"name": workflow.name}
        crud.update(session, Workflow, filter_dict, update_dict)

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
            workflows = self.workflow_loader.load_all_from_dir(session)
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
