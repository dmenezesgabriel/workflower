import logging

from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MAX_INSTANCES,
    EVENT_JOB_MISSED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_SUBMITTED,
)
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from workflower.adapters.scheduler import callbacks

logger = logging.getLogger("workflower.adapters.scheduler")


def create_sqlalchemy_jobstore(**kwargs):
    return SQLAlchemyJobStore(**kwargs)


def create_scheduler(jobstores, executors, timezone):
    scheduler = BackgroundScheduler()
    scheduler.configure(
        jobstores=jobstores,
        executors=executors,
        timezone=timezone,
    )

    def on_job_added(event):
        callbacks.job_added_callback(event)

    def on_job_executed(event):
        callbacks.job_executed_callback(event, scheduler)

    def on_job_error(event):
        callbacks.job_error_callback(event)

    def on_job_removed(event):
        callbacks.job_removed_callback(event)

    def on_job_submitted(event):
        callbacks.job_submitted_callback(event)

    def on_job_missed(event):
        callbacks.job_missed_callback(event)

    def on_job_max_instances(event):
        callbacks.job_max_instances_callback(event)

    event_actions = [
        {"func": on_job_added, "event": EVENT_JOB_ADDED},
        {"func": on_job_executed, "event": EVENT_JOB_EXECUTED},
        {"func": on_job_error, "event": EVENT_JOB_ERROR},
        {"func": on_job_removed, "event": EVENT_JOB_REMOVED},
        {"func": on_job_submitted, "event": EVENT_JOB_SUBMITTED},
        {"func": on_job_missed, "event": EVENT_JOB_MISSED},
        {
            "func": on_job_max_instances,
            "event": EVENT_JOB_MAX_INSTANCES,
        },
    ]
    for event_action in event_actions:
        scheduler.add_listener(
            event_action["func"],
            event_action["event"],
        )
    return scheduler
