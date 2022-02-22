from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class TestWorkflowMapper:
    def test_workflow_mapper_can_load_workflows(self, session):
        session.execute(
            """
            INSERT INTO workflow (name) VALUES
            ("test0"),
            ("test1"),
            ("test2")
            """
        )

        workflows = session.query(Workflow).all()
        assert workflows[0].name == "test0"
        assert workflows[1].name == "test1"
        assert workflows[2].name == "test2"

    def test_workflow_mapper_can_save_workflow(self, session):
        workflow = Workflow(name="test")
        session.add(workflow)
        session.commit()

        record = session.query(Workflow).first()
        assert record.name == "test"

    def test_workflow_mapper_can_save_workflow_jobs(self, session):
        job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )

        workflow = Workflow(name="test")
        workflow.add_job(job)

        session.add(workflow)
        session.commit()

        record = session.query(Workflow).first()
        assert record.jobs[0].name == "test"
        assert record.jobs[0].operator == "python"
        assert record.jobs[0].definition == {"trigger": "date"}


class TestJobMapper:
    def test_job_mapper_can_load_jobs(self, session):
        session.execute(
            """
            INSERT INTO job (name, operator, definition) VALUES
            ("test0", "python", '{"trigger": "date"}')
            """
        )
        jobs = session.query(Job).all()
        assert jobs[0].name == "test0"
        assert jobs[0].operator == "python"
        assert jobs[0].definition == {"trigger": "date"}

    def test_job_mapper_can_save_jobs(self, session):
        job = Job(
            name="test", operator="python", definition={"trigger": "date"}
        )
        session.add(job)
        session.commit()

        record = session.query(Job).first()
        assert record.name == "test"
        assert record.operator == "python"
        assert record.definition == {"trigger": "date"}

    def test_job_mapper_backpopulate_workflow(self, session):
        workflow = Workflow(name="test")
        session.add(workflow)
        session.commit()

        job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
            workflow=workflow,
        )
        session.add(job)
        session.commit()

        record = session.query(Workflow).first()
        assert record.jobs[0].name == "test"
        assert record.jobs[0].operator == "python"
        assert record.jobs[0].definition == {"trigger": "date"}
