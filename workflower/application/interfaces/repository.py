from abc import ABC, abstractclassmethod
from typing import List, Literal, Type, Union

from workflower.domain.entities.event import Event
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow

Model = Union[Type[Workflow], Type[Job], Type[Event]]
Entity = Union[Workflow, Job, Event]
Relationships = Literal["jobs"]


class Repository(ABC):
    """
    Port for defining Entities storage interface.
    """

    @abstractclassmethod
    def add(self, entity: Entity):
        raise NotImplementedError

    @abstractclassmethod
    def get(self):
        raise NotImplementedError

    @abstractclassmethod
    def list(self, entity: Entity) -> List[Entity]:
        raise NotImplementedError

    @abstractclassmethod
    def update(self, entity: Entity):
        raise NotImplementedError

    @abstractclassmethod
    def remove(self, entity: Entity):
        raise NotImplementedError
