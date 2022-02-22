from workflower.domain.entities.workflow import Workflow


class TestWorkflowEntity:
    def test_workflow_initialize_correclty(self):
        workflow = Workflow(name="test")
        assert isinstance(workflow, Workflow)
        assert workflow.name == "test"

    def test_workflow_initialize_correctly_from_dict(self):
        workflow_dict = {"name": "test"}
        workflow = Workflow.from_dict(workflow_dict)
        assert isinstance(workflow, Workflow)
        assert workflow.name == "test"
