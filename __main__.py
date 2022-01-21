import logging

from workflower import App
from workflower.log import setup_loggers

app = App()
setup_loggers()

logger = logging.getLogger("workflower")

if __name__ == "__main__":
    app.setup()
    app.init()
    logger.info("Starting Workflower")
    try:
        app.run()
    except KeyboardInterrupt:
        app.stop()
