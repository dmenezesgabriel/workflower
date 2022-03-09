import logging

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
    DeactivateWorkflowCommand,
    DeactivateWorkflowJobsCommand,
    UpdateModifiedWorkflowFileStateCommand,
    UpdateWorkflowFileExistsStateCommand,
)
from workflower.domain.entities.workflow import Workflow

logger = logging.getLogger("workflower.services.workflow")


class WorkflowRunnerService:
    def schedule_one_workflow_jobs(
        self,
        uow,
        workflow: Workflow,
        scheduler,
        executor="default",
        jobstore="default",
    ) -> None:
        """
        Schedule one workflow
        """
        logger.info(f"Trying to schedule {workflow.name}")
        if not workflow.file_exists:
            logger.info(
                f"{workflow.name} file has been removed, unscheduling jobs"
            )
            deactivate_workflow_command = DeactivateWorkflowCommand(
                uow, workflow.id
            )
            deactivate_workflow_command.execute()
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
                # Job should be scheduled to run immediately after it's
                # dependency
                if job.depends_on:
                    logger.debug(
                        f"Job {job.id} depends on {job.depends_on}, skipping."
                    )
                    continue
                # Job Already scheduled
                scheduled_job = scheduler.get_job(job.id)
                if scheduled_job:
                    logger.debug(f"Job {job.id} already added, skipping.")
                    next_run_time = scheduled_job.next_run_time
                    update_next_runtime_command = UpdateNextRunTimeCommand(
                        uow, job.id, next_run_time
                    )
                    update_next_runtime_command.execute()
                    continue
                # Job should be scheduled
                if job.is_active:
                    schedule_jobs_command = ScheduleJobCommand(
                        uow, job.id, scheduler, executor, jobstore
                    )
                    schedule_jobs_command.execute()

                    scheduled_job = scheduler.get_job(job.id)
                    if scheduled_job:
                        next_run_time = scheduled_job.next_run_time
                        update_next_runtime_command = UpdateNextRunTimeCommand(
                            uow, job.id, next_run_time
                        )
                        update_next_runtime_command.execute()

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

            # Load all workflows on database, including if the file has ben
            # removed.
            workflows = uow.workflows.list()
            for workflow in workflows:
                if not workflow.trigger == "on_schedule":
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
