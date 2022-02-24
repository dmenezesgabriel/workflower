from typing import Any

from workflower.adapters.sqlalchemy.repository import SqlAlchemyRepository
from workflower.application.interfaces.unit_of_work import UnitOfWork
from workflower.domain.entities.event import Event
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class SqlAlchemyUnitOfWork(UnitOfWork):
    """
    Secondary adapter providing implementation of transaction management for
    ORM SQLAlchemy.
    """

    def __init__(self, session):
        self.session = session

    def __enter__(self):
        self.workflows = SqlAlchemyRepository(self.session, model=Workflow)
        self.jobs = SqlAlchemyRepository(self.session, model=Job)
        self.events = SqlAlchemyRepository(self.session, model=Event)
        return self

    def __exit__(self, *args: Any):
        try:
            self.commit()
        except Exception:
            self.rollback()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
