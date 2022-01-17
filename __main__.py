from workflower import App

app = App()

if __name__ == "__main__":
    app.setup()
    try:
        app.run()
    except Exception:
        pass
    finally:
        # TODO
        # Abstract with app.stop()
        app.scheduler.shutdown()
