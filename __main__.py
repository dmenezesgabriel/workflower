import asyncio
import logging
import os
import signal
from concurrent.futures import ThreadPoolExecutor

import uvicorn

from workflower.api.client import create_app
from workflower.app import App
from workflower.log import setup_loggers

app = App()
api = create_app()
setup_loggers()

logger = logging.getLogger("workflower")


def raise_graceful_exit(*args):
    logger.debug(f"Got shutting down signal for PID={os.getpid()}")
    logger.debug("Gracefully shuting down")
    app.stop()
    loop = asyncio.get_event_loop()
    tasks = asyncio.all_tasks(loop=loop)
    for t in tasks:
        t.cancel()
    server.should_exit = True
    loop.stop()


if __name__ == "__main__":
    global server
    signal.signal(signal.SIGINT, raise_graceful_exit)
    signal.signal(signal.SIGBREAK, raise_graceful_exit)
    signal.signal(signal.SIGTERM, raise_graceful_exit)
    loop = asyncio.new_event_loop()
    app.setup()
    app.init()
    logger.info("Starting Workflower")
    config = uvicorn.Config(app=api)
    server = uvicorn.Server(config)
    executor = ThreadPoolExecutor(max_workers=1)
    loop.run_in_executor(executor, server.run)
    loop.create_task(app.run())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
