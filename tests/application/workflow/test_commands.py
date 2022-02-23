from workflower.application.workflow import commands


class TestCreateWorkflowCommand:
    def test_create_workflow_command(self, uow):
        command = commands.CreateWorkflowCommand(unit_of_work=uow)
        new_workflow = command.execute(name="test")

        new_workflow_id = new_workflow.id
        with uow:
            workflow = uow.workflows.get(id=new_workflow_id)
        assert workflow.name == "test"
