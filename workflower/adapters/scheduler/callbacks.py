import logging

from workflower.adapters.sqlalchemy.setup import Session
from workflower.adapters.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from workflower.application.event.commands import CreateEventCommand
from workflower.application.job.commands import (
    ChangeJobStatusCommand,
    GetDependencyTriggerJobsCommand,
    ScheduleJobCommand,
    UpdateNextRunTimeCommand,
)

logger = logging.getLogger("workflower.adapters.scheduler.callbacks")


def job_added_callback(event) -> None:
    session = Session()
    uow = SqlAlchemyUnitOfWork(session)
    create_event_command = CreateEventCommand(
        uow,
        name="job_added",
        model="job",
        model_id=event.job_id,
        exception=None,
        output=None,
    )
    create_event_command.execute()
    change_job_status_command = ChangeJobStatusCommand(
        uow, event.job_id, "added"
    )
    change_job_status_command.execute()


def job_missed_callback(event) -> None:
    session = Session()
    uow = SqlAlchemyUnitOfWork(session)
    create_event_command = CreateEventCommand(
        uow,
        name="job_missed",
        model="job",
        model_id=event.job_id,
        exception=None,
        output=None,
    )
    create_event_command.execute()
    change_job_status_command = ChangeJobStatusCommand(
        uow, event.job_id, "missed"
    )
    change_job_status_command.execute()


def job_max_instances_callback(event) -> None:
    session = Session()
    uow = SqlAlchemyUnitOfWork(session)
    create_event_command = CreateEventCommand(
        uow,
        name="job_max_instances",
        model="job",
        model_id=event.job_id,
        exception=None,
        output=None,
    )
    create_event_command.execute()
    logger.warning(f"Job{event.job_id} has reached max instances")


def job_submitted_callback(event) -> None:
    session = Session()
    uow = SqlAlchemyUnitOfWork(session)
    create_event_command = CreateEventCommand(
        uow,
        name="job_submitted",
        model="job",
        model_id=event.job_id,
        exception=None,
        output=None,
    )
    create_event_command.execute()
    change_job_status_command = ChangeJobStatusCommand(
        uow, event.job_id, "submitted"
    )
    change_job_status_command.execute()


def job_removed_callback(event) -> None:
    session = Session()
    uow = SqlAlchemyUnitOfWork(session)
    create_event_command = CreateEventCommand(
        uow,
        name="job_removed",
        model="job",
        model_id=event.job_id,
        exception=None,
        output=None,
    )
    create_event_command.execute()
    change_job_status_command = ChangeJobStatusCommand(
        uow, event.job_id, "removed"
    )
    change_job_status_command.execute()


def job_executed_callback(event, scheduler) -> None:
    """
    On job executed event.
    """
    session = Session()
    uow = SqlAlchemyUnitOfWork(session)
    create_event_command = CreateEventCommand(
        uow,
        name="job_executed",
        model="job",
        model_id=event.job_id,
        exception=None,
        output=event.retval,
    )
    change_job_status_command = ChangeJobStatusCommand(
        uow, event.job_id, "executed"
    )
    change_job_status_command.execute()
    create_event_command.execute()
    executed_job = scheduler.get_job(event.job_id)
    # Job may be removed after execution if does not has a continuos trigger
    if executed_job:
        next_run_time = executed_job.next_run_time
        update_next_runtime_command = UpdateNextRunTimeCommand(
            uow, event.job_id, next_run_time
        )
        update_next_runtime_command.execute()

    get_dependency_jobs_command = GetDependencyTriggerJobsCommand(
        uow, event.job_id, event.retval
    )
    dependency_jobs = get_dependency_jobs_command.execute()

    dependency_jobs
    for dependency_job in dependency_jobs:
        schedule_job_command = ScheduleJobCommand(
            uow,
            dependency_job.id,
            scheduler,
            job_return_value=event.retval,
        )
        schedule_job_command.execute()
        change_dependency_job_status_command = ChangeJobStatusCommand(
            uow, dependency_job.id, "scheduled"
        )
        change_dependency_job_status_command.execute()


def job_error_callback(event) -> None:
    session = Session()
    uow = SqlAlchemyUnitOfWork(session)
    create_event_command = CreateEventCommand(
        uow,
        name="job_error",
        model="job",
        model_id=event.job_id,
        exception=event.exception,
        output=None,
    )
    create_event_command.execute()
    change_job_status_command = ChangeJobStatusCommand(
        uow, event.job_id, "error"
    )
    change_job_status_command.execute()
