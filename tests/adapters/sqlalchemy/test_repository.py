from re import A

from workflower.adapters.sqlalchemy.repository import SqlAlchemyRepository
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class TestSqlAlchemyRepository:
    def test_repository_can_save_an_entity(self, session):

        assert session.query(Workflow).all() == []

        workflow = Workflow(name="test")
        repository = SqlAlchemyRepository(session, model=Workflow)
        repository.add(workflow)
        session.commit()

        assert len(session.query(Workflow).all()) == 1

        record = session.query(Workflow).first()
        assert record.name == "test"

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

        repository = SqlAlchemyRepository(session, model=Workflow)

        assert len(session.query(Workflow).all()) == 3

        workflows = repository.list()
        assert workflows[0].name == "test0"
        assert workflows[1].name == "test1"
        assert workflows[2].name == "test2"

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
        repository = SqlAlchemyRepository(session, model=Workflow)
        workflow = repository.get(id=1)
        repository.remove(workflow)
        new_session.commit()

        assert session.query(Workflow).all() == []
