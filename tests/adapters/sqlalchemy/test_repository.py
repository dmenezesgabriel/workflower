from workflower.adapters.sqlalchemy.repository import SqlAlchemyRepository
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class TestSqlAlchemyRepository:
    def test_repository_can_save_an_entity(self, session):
        workflow = Workflow(name="test")
        repository = SqlAlchemyRepository(session, model=Workflow)
        repository.add(workflow)
        session.commit()

        record = session.query(Workflow).first()
        assert record.name == "test"

    def test_repository_returns_an_entity(self, session):
        workflow = Workflow(name="test")
        session.add(workflow)
        session.commit()

        repository = SqlAlchemyRepository(session, model=Workflow)
        assert workflow.id == repository.get(id=workflow.id).id
