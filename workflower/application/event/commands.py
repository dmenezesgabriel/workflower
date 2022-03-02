import logging

from sqlalchemy.exc import IntegrityError
from workflower.application.interfaces.unit_of_work import UnitOfWork
from workflower.domain.entities.event import Event

logger = logging.getLogger("workflower.application.event.commands")


class CreateEventCommand:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        name: str,
        model: str,
        model_id: str,
        exception: str = None,
        output: str = None,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.name = name
        self.model = model
        self.model_id = model_id
        self.exception = exception
        self.output = output

    def execute(self):
        try:
            with self.unit_of_work as uow:
                event = Event(
                    self.name,
                    self.model,
                    self.model_id,
                    self.exception,
                    self.output,
                )
                uow.events.add(event)
                return event
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
