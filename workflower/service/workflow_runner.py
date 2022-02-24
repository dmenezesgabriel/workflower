import asyncio
import logging
import os

from workflower.adapters.sqlalchemy.setup import Session
from workflower.adapters.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from workflower.application.job.commands import (
    RemoveJobCommand,
    ScheduleJobCommand,
    UnscheduleJobCommand,
    UpdateNextRunTimeCommand,
)
from workflower.application.workflow.commands import (
    DeactivateWorkflowJobsCommand,
    UpdateModifiedWorkflowFileStateCommand,
    UpdateWorkflowFileExistsStateCommand,
)
from workflower.config import Config
from workflower.domain.entities.workflow import Workflow
from workflower.loader import WorkflowLoader

logger = logging.getLogger("workflower.service.workflow")


class WorkflowRunnerService:
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
        self, uow, workflow: Workflow, scheduler
    ) -> None:
        """
        Schedule one workflow
        """
        logger.info(f"Trying to schedule {workflow.name}")

        if not workflow.file_exists:
            logger.info(
                f"{workflow.name} file has been removed, unscheduling jobs"
            )
            workflow.is_active = False
            deactivate_workflow_jobs_command = DeactivateWorkflowJobsCommand(
                uow, workflow.id
            )
            deactivate_workflow_jobs_command.execute()
            for job in workflow.jobs:
                unschedule_job_command = UnscheduleJobCommand(
                    uow, job.id, scheduler
                )
                unschedule_job_command.execute()
            logger.info(f"{workflow.name} file removed, skipping")

        elif workflow.file_exists:
            if workflow.modified_since_last_load:
                logger.info(
                    f"{workflow.name} file has been modified, "
                    "unscheduling jobs"
                )
                for job in workflow.jobs:
                    unschedule_job_command = UnscheduleJobCommand(
                        uow, job.id, scheduler
                    )
                    unschedule_job_command.execute()

            logger.info("Scheduling jobs")
            for job in workflow.jobs:
                if job.is_active:
                    schedule_jobs_command = ScheduleJobCommand(
                        uow, job.id, scheduler
                    )
                    schedule_jobs_command.execute()
                    update_next_runtime_command = UpdateNextRunTimeCommand(
                        uow, job.id, scheduler
                    )
                    update_next_runtime_command.execute()

    def schedule_workflows_jobs(self, scheduler) -> None:
        """
        run Workflow Controller.
        """
        logger.info("Scheduling workflows jobs")
        session = Session()
        uow = SqlAlchemyUnitOfWork(session)
        with uow:
            # Load all workflows into database, it won't load if file has been
            # removed.

            # Clean dangling jobs
            jobs = uow.jobs.list()
            for job in jobs:
                if not job.is_active:
                    unschedule_job_command = UnscheduleJobCommand(
                        uow, job.id, scheduler
                    )
                    unschedule_job_command.execute()
                if not job.workflow:
                    remove_job_command = RemoveJobCommand(uow, job.id)
                    remove_job_command.execute()

            self.workflow_loader.load_all_from_dir(uow)
            # Load all workflows on database, including if the file has ben
            # removed.
            workflows = uow.workflows.list()
            for workflow in workflows:
                update_modified_file_state_command = (
                    UpdateModifiedWorkflowFileStateCommand(uow, workflow.id)
                )
                update_modified_file_state_command.execute()

                update_Workflow_file_exists_command = (
                    UpdateWorkflowFileExistsStateCommand(uow, workflow.id)
                )
                update_Workflow_file_exists_command.execute()
                self.schedule_one_workflow_jobs(uow, workflow, scheduler)

    async def run(self, scheduler):
        self.is_running = True
        while self.is_running:
            self.schedule_workflows_jobs(scheduler)
            logger.info(f"Sleeping {Config.CYCLE} seconds")
            await asyncio.sleep(Config.CYCLE)

    def stop(self):
        self.is_running = False
