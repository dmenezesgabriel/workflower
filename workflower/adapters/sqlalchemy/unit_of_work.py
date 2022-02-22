from typing import Any

from workflower.application.interfaces.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    """
    Secondary adapter providing implementation of transaction management for
    ORM SQLAlchemy.
    """

    def __init__(self, session):
        self.session = session

    def __enter__(self):
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
