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

    def test_workflows_mapper_can_save_workflow(self, session):
        workflow = Workflow(name="test")
        session.add(workflow)
        session.commit()

        record = session.query(Workflow).first()
        assert record.name == "test"


class TestJobMapper:
    pass
