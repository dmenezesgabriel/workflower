from workflower import App
from workflower.logger import app_logger

app = App()

if __name__ == "__main__":
    app.setup()
    app_logger.info("Starting Workflower")
    try:
        app.run()
    except KeyboardInterrupt:
        app.scheduler.shutdown()
