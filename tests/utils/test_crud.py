import unittest.mock
import uuid

import pytest
from config import Config
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from workflower.models.base import BaseModel
from workflower.utils import crud


@pytest.fixture(scope="function")
def session():
    """
    sqlalchemy.orm.session.Session.
    """
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


class DummyModel(BaseModel):
    __tablename__ = "test"
    name = Column(
        "name",
        String,
        unique=True,
        index=True,
    )

    def __init__(self, name):
        self.name = name


class TestCreate:
    def test_create_calls_session_add(cls, session):
        """
        crud.create should call sqlalchemy.orm.session.Session.add.
        """
        with unittest.mock.patch("sqlalchemy.orm.session.Session.add") as mock:
            name = str(uuid.uuid4())
            crud.create(session=session, model_object=DummyModel, name=name)
        assert mock.call_count == 1

    def test_create_calls_session_commit(cls, session):
        """
        crud.create should call sqlalchemy.orm.session.Session.commit.
        """
        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.commit"
        ) as mock:
            name = str(uuid.uuid4())
            crud.create(session=session, model_object=DummyModel, name=name)
        assert mock.call_count == 1

    def test_create_calls_session_refresh(cls, session):
        """
        crud.create should call sqlalchemy.orm.session.Session.refresh.
        """
        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.refresh"
        ) as mock:
            name = str(uuid.uuid4())
            crud.create(session=session, model_object=DummyModel, name=name)
        assert mock.call_count == 1

    def test_create_calls_session_rollback_on_exception(cls, session):
        """
        crud.create should call sqlalchemy.orm.session.Session.rollback.
        """
        # Mock commit exception
        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.commit"
        ) as mock_commit:
            mock_commit.side_effect = Exception("Mock Exception")
            #  Check if rollback is called
            with unittest.mock.patch(
                "sqlalchemy.orm.session.Session.rollback"
            ) as mock_rollback:
                name = str(uuid.uuid4())
                crud.create(
                    session=session, model_object=DummyModel, name=name
                )
            assert mock_rollback.call_count == 1

    # Integration tests
    def test_create_model_instance(cls, session):
        """
        Should create an Object with args passed matching with attributes.
        """
        name = str(uuid.uuid4())
        database_object = crud.create(
            session=session, model_object=DummyModel, name=name
        )
        assert isinstance(database_object, DummyModel)

    def test_create_model_attributes_match(cls, session):
        """
        Should create an Object which args passed matching with attributes.
        """
        name = str(uuid.uuid4())
        crud.create(session=session, model_object=DummyModel, name=name)
        assert (
            session.query(DummyModel).filter_by(name=name).first().name == name
        )


class TestGetOne:
    def test_get_one_calls_session_query(cls, session):
        """
        crud.get_one should call sqlalchemy.orm.session.Session.query.
        """
        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.query"
        ) as mock:
            name = str(uuid.uuid4())
            crud.get_one(session, DummyModel, name=name)
        assert mock.call_count == 1

    # Integration tests
    def test_get_one_model_instance(cls, session):
        """
        Should get an Object with correct class.
        """
        name = str(uuid.uuid4())
        object = DummyModel(name=name)
        session.add(object)
        session.commit()
        returned_object = crud.get_one(session, DummyModel, name=name)
        assert isinstance(returned_object, DummyModel)

    def test_get_one_attribute_match(cls, session):
        """
        Should get an Object which args passed matching with attributes.
        """
        name = str(uuid.uuid4())
        object = DummyModel(name=name)
        session.add(object)
        session.commit()
        crud.get_one(session, DummyModel, name=name)
        assert (
            session.query(DummyModel).filter_by(name=name).first().name == name
        )

    def test_get_one_not_exists(cls, session):
        """
        Should return none if searched object does not exists.
        """
        name = str(uuid.uuid4())
        object = DummyModel(name=name)
        session.add(object)
        session.commit()
        returned_object = crud.get_one(session, DummyModel, name="not_exists")
        assert returned_object is None


class TestGetAll:
    def test_get_all_calls_session_query(cls, session):
        """
        crud.get_one should call sqlalchemy.orm.session.Session.query.
        """
        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.query"
        ) as mock:
            crud.get_all(session, DummyModel)
        assert mock.call_count == 1

    # Integration tests
    def test_get_all(cls, session):
        """
        crud.get_all should get all objects from a given model.
        """
        for i in range(4, 10):
            name = str(uuid.uuid4())
            object = DummyModel(name=name)
            session.add(object)
            session.commit()
        result = crud.get_all(session, DummyModel)
        assert len(result) == 6


class TestUpdate:
    def test_update(cls, session):
        name = str(uuid.uuid4())
        object = DummyModel(name=name)
        session.add(object)
        session.commit()
        filter_dict = {"name": name}
        update_dict = {"name": "new_name"}
        crud.update(session, DummyModel, filter_dict, update_dict)
        assert (
            session.query(DummyModel).filter_by(name="new_name").first().name
            == "new_name"
        )


class TestDelete:
    def test_delete(cls, session):
        name = str(uuid.uuid4())
        object = DummyModel(name=name)
        session.add(object)
        session.commit()
        crud.delete(session, DummyModel, name=name)
        assert session.query(DummyModel).filter_by(name=name).first() is None
