import asyncio
import logging

from workflower.config import Config
from workflower.services.workflow.loader import WorkflowLoaderService
from workflower.services.workflow.runner import WorkflowRunnerService

logger = logging.getLogger("workflower.services.workflow")


class WorkflowController:
    """
    Workflow Controller.
    """

    def __init__(self) -> None:
        self.workflow_loader = WorkflowLoaderService()
        self.workflow_runner = WorkflowRunnerService()
        self.is_running = False

    async def run(self, scheduler):
        self.is_running = True
        while self.is_running:
            self.workflow_loader.load_all_from_dir()
            self.workflow_runner.schedule_workflows_jobs(scheduler)
            logger.info(f"Sleeping {Config.CYCLE} seconds")
            await asyncio.sleep(Config.CYCLE)

    def stop(self):
        self.is_running = False
