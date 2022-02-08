import asyncio
import logging
import os
import signal
from concurrent.futures import ThreadPoolExecutor

from workflower.api import create_api
from workflower.controllers.workflow import WorkflowContoller
from workflower.log import setup_loggers
from workflower.scheduler import SchedulerService
from workflower.server import create_server

scheduler_service = SchedulerService()
api = create_api()
server = create_server(api)
setup_loggers()
workflow_controller = WorkflowContoller()

logger = logging.getLogger("workflower")


def exit_handler(*args):
    logger.debug(f"Got shutting down signal for PID={os.getpid()}")
    logger.debug("Gracefully shuting down")
    workflow_controller.stop()
    scheduler_service.stop()
    loop = asyncio.get_event_loop()
    tasks = asyncio.all_tasks(loop=loop)
    for t in tasks:
        t.cancel()
    server.should_exit = True
    loop.stop()


def run():
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGBREAK, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    loop = asyncio.new_event_loop()
    scheduler_service.setup()
    scheduler_service.init()
    logger.info("Starting Workflower")
    executor = ThreadPoolExecutor(max_workers=1)
    loop.run_in_executor(executor, server.run)
    loop.create_task(scheduler_service.run())
    loop.create_task(workflow_controller.run(scheduler_service.scheduler))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
