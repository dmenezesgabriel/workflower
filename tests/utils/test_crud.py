import unittest.mock
import uuid

import pytest
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from workflower.models.base import BaseModel
from workflower.models.workflow import Workflow
from workflower.utils import crud


@pytest.fixture(scope="function")
def session():
    engine = create_engine(Config.APP_DATABASE_URL)
    BaseModel.metadata.create_all(bind=engine)
    Session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()
        BaseModel.metadata.drop_all(bind=engine)


class TestCreate:
    def test_create_calls_add(cls, session):
        print(type(session))
        with unittest.mock.patch("sqlalchemy.orm.session.Session.add") as mock:
            name = str(uuid.uuid4())
            crud.create(session=session, model_object=Workflow, name=name)
        assert mock.call_count == 1

    def test_create_calls_commit(cls, session):
        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.commit"
        ) as mock:
            name = str(uuid.uuid4())
            crud.create(session=session, model_object=Workflow, name=name)
        assert mock.call_count == 1

    def test_create_calls_refresh(cls, session):
        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.refresh"
        ) as mock:
            name = str(uuid.uuid4())
            crud.create(session=session, model_object=Workflow, name=name)
        assert mock.call_count == 1

    def test_create_success(cls, session):
        name = str(uuid.uuid4())
        database_object = crud.create(
            session=session, model_object=Workflow, name=name
        )
        assert isinstance(database_object, Workflow)
        assert (
            session.query(Workflow).filter_by(name=name).first().name == name
        )

    def test_create_wrong_attribute(cls, session):
        with pytest.raises(TypeError):
            crud.create(
                session=session,
                model_object=Workflow,
                wrong_attribute="wrong_attribute",
            )


class TestGetOne:
    def test_get_one(cls, session):
        name = str(uuid.uuid4())
        object = Workflow(name=name)
        session.add(object)
        session.commit()
        returned_object = crud.get_one(session, Workflow, name=name)
        assert isinstance(returned_object, Workflow)
        assert (
            session.query(Workflow).filter_by(name=name).first().name == name
        )

    def test_get_one_not_exists(cls, session):
        name = str(uuid.uuid4())
        object = Workflow(name=name)
        session.add(object)
        session.commit()
        returned_object = crud.get_one(session, Workflow, name="not_exists")
        assert returned_object is None


class TestGetAll:
    def test_get_all(cls, session):
        for i in range(4, 10):
            name = str(uuid.uuid4())
            object = Workflow(name=name)
            session.add(object)
            session.commit()
        result = crud.get_all(session, Workflow)
        assert len(result) == 6


class TestUpdate:
    def test_update(cls, session):
        name = str(uuid.uuid4())
        object = Workflow(name=name)
        session.add(object)
        session.commit()
        filter_dict = {"name": name}
        update_dict = {"name": "new_name"}
        crud.update(session, Workflow, filter_dict, update_dict)
        assert (
            session.query(Workflow).filter_by(name="new_name").first().name
            == "new_name"
        )


class TestDelete:
    def test_delete(cls, session):
        name = str(uuid.uuid4())
        object = Workflow(name=name)
        session.add(object)
        session.commit()
        crud.delete(session, Workflow, name=name)
        assert session.query(Workflow).filter_by(name=name).first() is None
