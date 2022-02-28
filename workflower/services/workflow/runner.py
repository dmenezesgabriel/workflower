import asyncio
import logging
import os

from workflower.adapters.sqlalchemy.backup import backup_sqlite, dump_sqlite
from workflower.adapters.sqlalchemy.setup import Session
from workflower.adapters.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from workflower.application.event.commands import CreateEventCommand
from workflower.application.job.commands import (
    ChangeJobStatusCommand,
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
from workflower.services.workflow.loader import WorkflowLoader

logger = logging.getLogger("workflower.services.workflow")


class WorkflowRunnerService:
    """
    Workflow Controller.
    """

    def __init__(self) -> None:
        self.workflow_loader = WorkflowLoader()
        self.is_running = False
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
        if not workflow.is_active:
            deactivate_workflow_jobs_command = DeactivateWorkflowJobsCommand(
                uow, workflow.id
            )
            deactivate_workflow_jobs_command.execute()
            for job in workflow.jobs:
                unschedule_job_command = UnscheduleJobCommand(
                    uow, job.id, scheduler
                )
                unschedule_job_command.execute()
                change_job_status_command = ChangeJobStatusCommand(
                    uow, job.id, "unscheduled"
                )
                change_job_status_command.execute()
                create_event_command = CreateEventCommand(
                    uow,
                    name="job_unscheduled",
                    model="job",
                    model_id=job.id,
                    exception=None,
                    output=None,
                )
                create_event_command.execute()
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
                    change_job_status_command = ChangeJobStatusCommand(
                        uow, job.id, "unscheduled"
                    )
                    change_job_status_command.execute()
                    create_event_command = CreateEventCommand(
                        uow,
                        name="job_unscheduled",
                        model="job",
                        model_id=job.id,
                        exception=None,
                        output=None,
                    )
                    create_event_command.execute()
            logger.info("Scheduling jobs")
            for job in workflow.jobs:
                if job.depends_on:
                    logger.debug(
                        f"Job {job.id} depends on {job.depends_on}, skipping."
                    )
                    continue
                if job.is_active:
                    schedule_jobs_command = ScheduleJobCommand(
                        uow, job.id, scheduler
                    )
                    schedule_jobs_command.execute()

                    scheduled_job = scheduler.get_job(job.id)
                    if scheduled_job:
                        next_run_time = scheduled_job.next_run_time
                        update_next_runtime_command = UpdateNextRunTimeCommand(
                            uow, job.id, next_run_time
                        )
                        update_next_runtime_command.execute()

                    if job.status != "scheduled":
                        create_event_command = CreateEventCommand(
                            uow,
                            name="job_scheduled",
                            model="job",
                            model_id=job.id,
                            exception=None,
                            output=None,
                        )
                        create_event_command.execute()
                        change_job_status_command = ChangeJobStatusCommand(
                            uow, job.id, "scheduled"
                        )
                        change_job_status_command.execute()

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
                    change_job_status_command = ChangeJobStatusCommand(
                        uow, job.id, "unscheduled"
                    )
                    change_job_status_command.execute()
                    create_event_command = CreateEventCommand(
                        uow,
                        name="job_unscheduled",
                        model="job",
                        model_id=job.id,
                        exception=None,
                        output=None,
                    )
                    create_event_command.execute()
                if not job.workflow:
                    remove_job_command = RemoveJobCommand(uow, job.id)
                    remove_job_command.execute()

            self.workflow_loader.load_all_from_dir(uow)
            # Load all workflows on database, including if the file has ben
            # removed.
            workflows = uow.workflows.list()
            for workflow in workflows:
                if not workflow.trigger == "automatic":
                    continue
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
            # Backup sqlite
            backup_sqlite(
                Config.APP_DATABASE_URL, Config.APP_DATABASE_BACKUP_URL
            )
            dump_sqlite(Config.SQLITE_DATABASE_DUMP_PATH)

    def stop(self):
        self.is_running = False
