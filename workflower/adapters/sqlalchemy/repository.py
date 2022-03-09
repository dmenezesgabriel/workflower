import logging

from workflower.application.interfaces.repository import (
    Entity,
    Model,
    Repository,
)

from sqlalchemy.orm.session import Session

logger = logging.getLogger("workflower.adapters.repository")


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
        logger.debug(f"Adding {object}")

        self.session.add(object)

    def get(self, **kwargs):
        """
        Get one object from database.
        """
        return self.session.query(self.model).filter_by(**kwargs).first()

    def list(self, **kwargs):
        """
        Get list of objects of a model type.
        """
        return self.session.query(self.model).filter_by(**kwargs).all()

    def update(self, filter_dict: dict, new_attributes_dict: dict):
        """
        Update a object of model type.
        """
        logger.debug(f"Updating {self.model}, {dict(**filter_dict)}")
        self.session.query(self.model).filter_by(**filter_dict).update(
            new_attributes_dict
        )

    def remove(self, entity: Entity):
        """
        Remove a object of model type.
        """
        logger.debug(f"Deleting {entity}")
        self.session.delete(entity)
