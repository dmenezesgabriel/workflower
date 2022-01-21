from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from workflower.database import DatabaseManager
from workflower.utils import crud

database = DatabaseManager()

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    @classmethod
    def create(cls, **kwargs):
        with database.session_scope() as session:
            object = crud.create(session, cls, **kwargs)
        return object

    @classmethod
    def get_one(cls, **kwargs):
        with database.session_scope() as session:
            object = crud.get_one(session, cls, **kwargs)
        return object

    @classmethod
    def get_all(cls, **kwargs):
        with database.session_scope() as session:
            object = crud.get_all(session, cls, **kwargs)
        return object

    @classmethod
    def update(cls, filter_dict, new_attributes_dict):
        with database.session_scope() as session:
            crud.update(session, cls, filter_dict, new_attributes_dict)

    @classmethod
    def delete(cls, **kwargs):
        with database.session_scope() as session:
            crud.delete(session, cls, **kwargs)

    @classmethod
    def get_or_create(cls, **kwargs):
        with database.session_scope() as session:
            object = crud.get_or_create(session, cls, **kwargs)
        return object
