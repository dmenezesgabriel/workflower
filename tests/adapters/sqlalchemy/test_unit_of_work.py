import unittest
import unittest.mock

from workflower.adapters.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class TestSqlAlchemyUnitOfWork:
    def test_unif_of_work_calls_session_commit(self, session):

        uow = SqlAlchemyUnitOfWork(session)

        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.commit"
        ) as mock:
            with uow:
                workflow = Workflow(name="test")
                uow.workflows.add(workflow)
        assert mock.call_count == 1

    def test_unit_of_work_can_retrieve_workflow_and_add_a_job_on_it(
        self, session_factory
    ):
        first_session = session_factory()

        assert first_session.query(Workflow).all() == []
        assert first_session.query(Job).all() == []

        workflow = Workflow(name="test")
        first_session.add(workflow)
        first_session.commit()

        assert len(first_session.query(Workflow).all()) == 1

        second_session = session_factory()
        uow = SqlAlchemyUnitOfWork(second_session)
        with uow:

            workflow = second_session.query(Workflow).filter_by(id=1).first()

            job = Job(
                name="test",
                operator="python",
                definition={"trigger": "date"},
            )

            workflow.add_job(job)

            assert len(second_session.query(Job).all()) == 1

            record = second_session.query(Workflow).first()

            assert record.jobs[0].name == "test"
            assert record.jobs[0].operator == "python"
            assert record.jobs[0].definition == {"trigger": "date"}

    def test_unit_of_work_rolls_back_transaction_on_error(
        self, session_factory
    ):
        first_session = session_factory()
        uow = SqlAlchemyUnitOfWork(first_session)

        with unittest.mock.patch(
            "sqlalchemy.orm.session.Session.commit"
        ) as mock_commit:
            mock_commit.side_effect = Exception("Mock Exception")
            #  Check if rollback is called
            with unittest.mock.patch(
                "sqlalchemy.orm.session.Session.rollback"
            ) as mock_rollback:
                with uow:
                    workflow = Workflow(name="test")
                    uow.workflows.add(workflow)
            assert mock_rollback.call_count == 1
