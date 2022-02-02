import asyncio
import logging
import os
import signal
from concurrent.futures import ThreadPoolExecutor

from workflower.api import create_api
from workflower.log import setup_loggers
from workflower.scheduler import create_scheduler
from workflower.server import create_server

scheduler = create_scheduler()
api = create_api()
server = create_server(api)
setup_loggers()

logger = logging.getLogger("workflower")


def exit_handler(*args):
    logger.debug(f"Got shutting down signal for PID={os.getpid()}")
    logger.debug("Gracefully shuting down")
    scheduler.stop()
    loop = asyncio.get_event_loop()
    tasks = asyncio.all_tasks(loop=loop)
    for t in tasks:
        t.cancel()
    server.should_exit = True
    loop.stop()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGBREAK, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    loop = asyncio.new_event_loop()
    scheduler.setup()
    scheduler.init()
    logger.info("Starting Workflower")
    executor = ThreadPoolExecutor(max_workers=1)
    loop.run_in_executor(executor, server.run)
    loop.create_task(scheduler.run())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
