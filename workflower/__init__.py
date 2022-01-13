import logging
import os
import time

import yaml
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from pytz import utc

from workflower.alteryx import run_workflow

logging.basicConfig()

jobstores = {
    "default": SQLAlchemyJobStore(url=Config.JOB_DATABASE_URL),
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


def run():
    while True:
        print("Loading Workflows")
        for root, dirs, files in os.walk(Config.WORKFLOWS_CONFIG_PATH):
            for file in files:
                if file.endswith(".yml"):
                    workflow_yaml_config_path = os.path.join(root, file)
                    with open(workflow_yaml_config_path) as yf:
                        configuration_dict = yaml.safe_load(yf)
                    workflow_name = configuration_dict["name"]
                    workflow_path = configuration_dict["path"]
                    print(f"Scheduling {workflow_name}")
                    try:
                        scheduler.add_job(
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
