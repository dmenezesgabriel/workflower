import unittest.mock

from workflower.adapters.sqlalchemy.repository import SqlAlchemyRepository
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class TestSqlAlchemyRepository:
    def test_repository_add_calls_session_add(cls, session):
        assert session.query(Workflow).all() == []
        with unittest.mock.patch("sqlalchemy.orm.session.Session.add") as mock:
            workflow = Workflow(name="test")
            repository = SqlAlchemyRepository(session, model=Workflow)
            repository.add(workflow)
        assert mock.call_count == 1

    def test_repository_can_save_an_entity(self, session):

        assert session.query(Workflow).all() == []

        workflow = Workflow(name="test")
        repository = SqlAlchemyRepository(session, model=Workflow)
        repository.add(workflow)
        session.commit()

        assert len(session.query(Workflow).all()) == 1

        record = session.query(Workflow).first()
        assert record.name == "test"

    def test_repository_get_calls_session_query(cls, session):
        workflow = Workflow(name="test")
        session.add(workflow)
        session.commit()

        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.query"
        ) as mock:
            repository = SqlAlchemyRepository(session, model=Workflow)
            repository.get(id=workflow.id).id
        assert mock.call_count == 1

    def test_repository_returns_an_entity(self, session):

        assert session.query(Workflow).all() == []

        workflow = Workflow(name="test")
        session.add(workflow)
        session.commit()

        repository = SqlAlchemyRepository(session, model=Workflow)

        assert len(session.query(Workflow).all()) == 1
        assert workflow.id == repository.get(id=workflow.id).id

    def test_repository_returns_an_entity_with_relationships(self, session):

        assert session.query(Workflow).all() == []
        assert session.query(Job).all() == []

        job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )

        workflow = Workflow(name="test")
        workflow.add_job(job)

        session.add(workflow)
        session.commit()

        repository = SqlAlchemyRepository(session, model=Workflow)

        assert len(session.query(Workflow).all()) == 1
        assert len(session.query(Job).all()) == 1

        record = repository.get(id=workflow.id)
        assert record.jobs[0].name == "test"
        assert record.jobs[0].operator == "python"
        assert record.jobs[0].definition == {"trigger": "date"}

    def test_repository_list_calls_session_query(cls, session):
        workflow = Workflow(name="test")
        session.add(workflow)
        session.commit()

        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.query"
        ) as mock:
            repository = SqlAlchemyRepository(session, model=Workflow)
            repository.list()
        assert mock.call_count == 1

    def test_repository_return_a_list_of_entities(self, session):

        assert session.query(Workflow).all() == []

        session.execute(
            """
            INSERT INTO workflow (name) VALUES
            ("test0"),
            ("test1"),
            ("test2")
            """
        )
        session.commit()

    def test_repository_update_calls_session_query(cls, session_factory):
        first_session = session_factory()

        assert first_session.query(Workflow).all() == []

        first_session.execute(
            """
            INSERT INTO workflow (name) VALUES
            ("test0")
            """
        )
        first_session.commit()

        assert len(first_session.query(Workflow).all()) == 1
        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.query"
        ) as mock:
            second_session = session_factory()
            repository = SqlAlchemyRepository(second_session, model=Workflow)
            repository.update(dict(id=1), dict(name="new_name"))
        assert mock.call_count == 1

    def test_repository_update_entity(self, session_factory):
        first_session = session_factory()

        assert first_session.query(Workflow).all() == []

        first_session.execute(
            """
            INSERT INTO workflow (name) VALUES
            ("test0")
            """
        )
        first_session.commit()

        assert len(first_session.query(Workflow).all()) == 1

        second_session = session_factory()

        repository = SqlAlchemyRepository(second_session, model=Workflow)
        repository.update(dict(id=1), dict(name="new_name"))
        second_session.commit()

        third_session = session_factory()
        second_repository = SqlAlchemyRepository(third_session, model=Workflow)
        record = second_repository.get(id=1)
        record.name == "new_name"

    def test_repository_remove_calls_session_delete(cls, session_factory):
        session = session_factory()

        assert session.query(Workflow).all() == []

        session.execute(
            """
            INSERT INTO workflow (name) VALUES
            ("test0")
            """
        )
        session.commit()

        assert len(session.query(Workflow).all()) == 1

        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.delete"
        ) as mock:
            new_session = session_factory()
            repository = SqlAlchemyRepository(new_session, model=Workflow)
            workflow = repository.get(id=1)
            repository.remove(workflow)
        assert mock.call_count == 1

    def test_repository_deletes_entity(self, session_factory):
        session = session_factory()

        assert session.query(Workflow).all() == []

        session.execute(
            """
            INSERT INTO workflow (name) VALUES
            ("test0")
            """
        )
        session.commit()

        assert len(session.query(Workflow).all()) == 1

        new_session = session_factory()
        repository = SqlAlchemyRepository(new_session, model=Workflow)
        workflow = repository.get(id=1)
        repository.remove(workflow)
        new_session.commit()

        assert session.query(Workflow).all() == []
