import os

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
        file_path = str(workflow_file)
        new_workflow = Workflow(name="test", file_path=file_path)
        with uow:
            uow.workflows.add(new_workflow)

        command = commands.UpdateModifiedWorkflowFileStateCommand(
            unit_of_work=uow
        )

        command.execute(new_workflow.id)
        session = session_factory()
        workflow = (
            session.query(Workflow).filter_by(id=new_workflow.id).first()
        )
        assert workflow.file_last_modified_at == str(
            os.path.getmtime(file_path)
        )

    def test_update_modified_file_state_command_updates_modified_since_load_f(
        self, session_factory, workflow_file, uow
    ):
        file_path = str(workflow_file)
        new_workflow = Workflow(name="test", file_path=file_path)
        with uow:
            uow.workflows.add(new_workflow)

        command = commands.UpdateModifiedWorkflowFileStateCommand(
            unit_of_work=uow
        )

        command.execute(new_workflow.id)
        session = session_factory()
        workflow = (
            session.query(Workflow).filter_by(id=new_workflow.id).first()
        )
        assert workflow.modified_since_last_load is False

    def test_update_modified_file_state_command_updates_modified_since_load_t(
        self, session_factory, workflow_file, uow
    ):
        file_path = str(workflow_file)
        new_workflow = Workflow(name="test", file_path=file_path)
        with uow:
            uow.workflows.add(new_workflow)

        command = commands.UpdateModifiedWorkflowFileStateCommand(
            unit_of_work=uow
        )

        command.execute(new_workflow.id)

        with open(file_path, "a") as f:
            f.write("new line\n")

        command.execute(new_workflow.id)

        session = session_factory()
        workflow = (
            session.query(Workflow).filter_by(id=new_workflow.id).first()
        )

        assert workflow.modified_since_last_load is True
