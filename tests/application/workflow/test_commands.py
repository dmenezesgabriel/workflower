from workflower.application.workflow import commands
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class TestCreateWorkflowCommand:
    def test_create_workflow_command_executes_correctly(self, uow):
        command = commands.CreateWorkflowCommand(unit_of_work=uow)
        new_workflow = command.execute(name="test")

        new_workflow_id = new_workflow.id
        with uow:
            workflow = uow.workflows.get(id=new_workflow_id)
        assert workflow.name == "test"


class TestAddWorkflowJobCommand:
    def test_add_job_to_workflow_command_executes_correctly(
        self, session_factory, uow
    ):
        workflow = Workflow(name="test")
        job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )

        with uow:
            uow.workflows.add(workflow)
            uow.jobs.add(job)

        command = commands.AddWorkflowJobCommand(unit_of_work=uow)
        command.execute(workflow_id=workflow.id, job_id=job.id)

        session = session_factory()
        assert len(session.query(Workflow).all()) == 1

        workflows = session.query(Workflow).all()
        assert workflows[0].name == "test"
        assert workflows[0].jobs[0].name == "test"
        assert workflows[0].jobs[0].operator == "python"
        assert workflows[0].jobs[0].definition == {"trigger": "date"}


class TestUpdateModifiedWorkflowFileStateCommand:
    def test_update_modified_file_state_command_updates_file_last_modified_at(
        self, session_factory, workflow_file, uow
    ):
        workflow = Workflow(name="test", file_path=str(workflow_file))
        with uow:
            uow.workflows.add(workflow)

        command = commands.UpdateModifiedWorkflowFileStateCommand(
            unit_of_work=uow
        )

        command.execute(workflow.id)
        print(workflow)
