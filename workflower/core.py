import asyncio
import logging
import os
import signal
from concurrent.futures import ThreadPoolExecutor

from workflower.adapters.scheduler.setup import scheduler
from workflower.adapters.server import create_server
from workflower.api import create_api
from workflower.services.workflow.runner import WorkflowRunnerService

api = create_api()
server = create_server(api)

workflow_controller = WorkflowRunnerService()

logger = logging.getLogger("workflower")


def exit_handler(*args):
    logger.debug(f"Got shutting down signal for PID={os.getpid()}")
    logger.info("Gracefully shuting down")
    workflow_controller.stop()
    scheduler.shutdown()
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
    logger.info("Starting Workflower")
    executor = ThreadPoolExecutor(max_workers=1)
    loop.run_in_executor(executor, server.run)
    scheduler.start()
    loop.create_task(workflow_controller.run(scheduler))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
