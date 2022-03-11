import asyncio
import logging
import os
import signal
from concurrent.futures import ThreadPoolExecutor

from workflower.adapters.api import create_api
from workflower.adapters.scheduler.setup import (
    create_scheduler,
    create_sqlalchemy_jobstore,
)
from workflower.adapters.server import create_server
from workflower.adapters.sqlalchemy.setup import engine
from workflower.config import Config
from workflower.controllers.workflow import WorkflowController

jobstores = dict(
    default=create_sqlalchemy_jobstore(
        engine=engine, tablename="on_schedule_jobs"
    ),
)
executors = dict(
    default={
        "type": "processpool",
        "max_workers": 50,
    },
)
job_defaults = dict(
    # No matter how much instances are late of same job, execute one only
    coalesce=True,
    # 10 minutos of tolerance for missed jobs
    misfire_grace_time=10 * 60,
)

scheduler = create_scheduler(
    executors=executors,
    jobstores=jobstores,
    timezone=Config.TIME_ZONE,
    job_defaults=job_defaults,
)

api = create_api()
server = create_server(api)
workflow_controller = WorkflowController()

logger = logging.getLogger("workflower")


def exit_handler(*args):
    logger.debug(f"Got shutting down signal for PID={os.getpid()}")
    logger.info("Gracefully shuting down")
    workflow_controller.stop()
    loop = asyncio.get_event_loop()
    tasks = asyncio.all_tasks(loop=loop)
    for t in tasks:
        t.cancel()
    server.should_exit = True
    loop.stop()


def start():
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    loop = asyncio.new_event_loop()
    logger.info("Starting Workflower")
    executor = ThreadPoolExecutor(max_workers=1)
    loop.run_in_executor(executor, server.run)
    scheduler.start()
    loop.create_task(workflow_controller.run(scheduler))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
