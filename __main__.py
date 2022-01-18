import logging

from workflower import App
from workflower.log import setup_loggers

app = App()

if __name__ == "__main__":
    setup_loggers()
    logger = logging.getLogger("workflower")
    app.setup()
    logger.info("Starting Workflower")
    try:
        app.run()
    except KeyboardInterrupt:
        app.scheduler.shutdown()
