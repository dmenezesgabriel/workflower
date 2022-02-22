from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class TestWorkflowMapper:
    def test_workflow_mapper_can_load_workflows(Self, session):
        session.execute(
            """
            INSERT INTO workflow (name) VALUES
            ("test")
        """
        )

        workflows = session.query(Workflow).all()
        print(workflows)
