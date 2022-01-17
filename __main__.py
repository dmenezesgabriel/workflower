from workflower import App

app = App()

if __name__ == "__main__":
    app.setup()
    try:
        app.run()
    except KeyboardInterrupt:
        app.scheduler.shutdown()
