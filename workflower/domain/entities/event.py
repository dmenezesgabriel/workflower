import logging

logger = logging.getLogger("workflower.models.event")


class Event:
    """
    Domain object for events.
    """

    def __init__(self, name, model, model_id, exception, output):
        self.name = name
        self.model = model
        self.model_id = model_id
        self.exception = exception
        self.output = output

    def __repr__(self) -> str:
        return (
            f"Event(name={self.name}, "
            f"model={self.model}, "
            f"model_id={self.model_id})"
        )
