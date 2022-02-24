import logging

logger = logging.getLogger("workflower.domain.entities.event")


class Event:
    """
    Domain object for events.

    Args:
        - name (str): Name of the given event.
        - model (str): event model.
        - model_id (str): event model_id.
        - exception (str, optional): exceptions.
        - output (str, optional): output.
    """

    def __init__(
        self,
        name: str,
        model: str,
        model_id: str,
        exception: str = None,
        output: str = None,
    ) -> None:
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
