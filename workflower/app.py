import json
import logging
import time

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from alteryx import run_workflow

logging.basicConfig()

jobstores = {
    "default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite"),
}
executors = {
    "default": {"type": "threadpool", "max_workers": 20},
}


def job_runs(event):
    if event.exception:
        print("job did not run")
    else:
        print("job completed")


def job_return_val(event):
    return event.retval


scheduler = BackgroundScheduler()
scheduler.add_listener(job_runs, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
scheduler.add_listener(job_return_val, EVENT_JOB_EXECUTED)
scheduler.configure(
    jobstores=jobstores,
    executors=executors,
    timezone=utc,
)

scheduler.start()

while True:
    print("Loading Workflows")
    with open("config.json") as f:
        workflows = json.load(f)
    for workflow in workflows:
        workflow_name = workflow["name"]
        workflow_path = workflow["path"]
        print(f"Scheduling {workflow_name}")
        try:
            job = scheduler.add_job(
                func=run_workflow,
                trigger="interval",
                minutes=1,
                id=workflow_name,
                args=[workflow_path],
                executor="default",
            )
        except ConflictingIdError:
            print(f"{workflow_name}, already scheduled")
            continue
    scheduler.print_jobs()
    time.sleep(5)
