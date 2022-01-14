import logging
import os
import time

import yaml
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from pytz import utc

from workflower import job

logging.basicConfig()

# TODO
# Move to config file
jobstores = {
    "default": SQLAlchemyJobStore(url=Config.JOB_DATABASE_URL),
}
executors = {
    "default": {"type": "threadpool", "max_workers": 20},
}


# TODO
# Make an workflow dependencies check event
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


def run():
    scheduler.start()
    while True:
        print("Loading Workflows")
        # TODO
        # Move to a modules loader
        for root, dirs, files in os.walk(Config.WORKFLOWS_CONFIG_PATH):
            for file in files:
                if file.endswith(".yml"):
                    workflow_yaml_config_path = os.path.join(root, file)
                    with open(workflow_yaml_config_path) as yf:
                        configuration_dict = yaml.safe_load(yf)
                    job.schedule_one(scheduler, configuration_dict)
        scheduler.print_jobs()
        time.sleep(Config.CYCLE)
