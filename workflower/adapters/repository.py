import logging
from abc import ABC, abstractclassmethod
from typing import List, Literal, Type, Union

from pytest import Session
from workflower.domain.entities.event import Event
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow

Model = Union[Type[Workflow], Type[Job], Type[Event]]
Entity = Union[Workflow, Job, Event]
Relationships = Literal["jobs"]

logger = logging.getLogger("workflower.adapters.repository")


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


class SqlAlchemyRepository(Repository):
    """
    SQLAlchemy repository, which enables basic operations with the database and
    the selected model.

    Args:
        - session (sqlalchemy.orm.session.Session): Session object from
        sqlalchemy that enables communication with the database.
        - model (Model): One of the classes that are used in domain layer.
    """

    def __init__(self, session: Session, model: Model):
        self.session = session
        self.model = model

    def add(self, object: Entity) -> None:
        """
        Add entity object to database.

        Args
            - object (Entity): Entity object.
        """
        try:
            self.session.add(object)
            self.session.commit()
            self.session.refresh(object)
            logger.debug(f"Object {object}  saved on database")
        except Exception as error:
            logger.error(f"Writting object {object}  failed. Error: {error}")
            self.session.rollback()

    def get(self, **kwargs):
        """
        Get one object from database.
        """
        logger.info(f"Getting {self.model} , {dict(**kwargs)}")
        return self.session.query(self.model).filter_by(**kwargs).first()

    def list(self, **kwargs) -> List[Entity]:
        """
        Get list of objects of a model type.
        """
        return self.session.query(self.model).filter_by(**kwargs).all()

    def update(self, filter_dict: dict, new_attributes_dict: dict):
        """
        Update a object of model type.
        """
        try:
            self.session.query(self.model).filter_by(**filter_dict).update(
                new_attributes_dict
            )
            self.session.commit()
            logger.debug(f"Model {self.model} , {dict(**filter_dict)} updated")
        except Exception as error:
            logger.error(
                f"Updating model_object{self.model} , {dict(**filter_dict)} "
                f"failed. Error: {error}"
            )

    def remove(self, entity: Entity):
        """
        Remove a object of model type.
        """
        logger.debug(f"Deleting {entity}")
        self.session.delete(entity)
        self.session.commit()
