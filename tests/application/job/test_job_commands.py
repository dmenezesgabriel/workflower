from datetime import datetime

from workflower.application.job import commands
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class TestCreateJobCommand:
    def test_create_workflow_command_executes_correctly(self, uow):
        command = commands.CreateJobCommand(
            unit_of_work=uow,
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )
        new_job = command.execute()

        new_job_id = new_job.id
        with uow:
            job = uow.jobs.get(id=new_job_id)
        assert job.name == "test"
        assert job.operator == "python"


class TestDeactivateJobCommand:
    def test_create_workflow_command_executes_correctly(
        self, session_factory, uow
    ):
        new_workflow = Workflow(name="test")
        new_job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )

        with uow:
            uow.workflows.add(new_workflow)
            uow.jobs.add(new_job)
            new_workflow.add_job(new_job)

        command = commands.DeactivateJobCommand(uow, new_job.id)
        command.execute()

        session = session_factory()
        job = session.query(Job).filter_by(id=new_job.id).first()
        assert job.is_active is False


class TestChangeJobStatusCommand:
    def test_create_workflow_command_executes_correctly(
        self, session_factory, uow
    ):
        new_workflow = Workflow(name="test")
        new_job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )

        with uow:
            uow.workflows.add(new_workflow)
            uow.jobs.add(new_job)
            new_workflow.add_job(new_job)

        command = commands.ChangeJobStatusCommand(uow, new_job.id, "scheduled")
        command.execute()

        session = session_factory()
        job = session.query(Job).filter_by(id=new_job.id).first()
        assert job.status == "scheduled"


class TestUpdateNextRunTimeCommand:
    def test_create_workflow_command_executes_correctly(
        self, session_factory, uow
    ):
        new_workflow = Workflow(name="test")
        new_job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )

        with uow:
            uow.workflows.add(new_workflow)
            uow.jobs.add(new_job)
            new_workflow.add_job(new_job)

        next_run_time = str(datetime.now())
        command = commands.UpdateNextRunTimeCommand(
            uow, new_job.id, next_run_time
        )
        command.execute()

        session = session_factory()
        job = session.query(Job).filter_by(id=new_job.id).first()
        assert job.next_run_time == next_run_time


class RemoveJobCommand:
    def test_create_workflow_command_executes_correctly(
        self, session_factory, uow
    ):
        new_workflow = Workflow(name="test")
        new_job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )

        with uow:
            uow.workflows.add(new_workflow)
            uow.jobs.add(new_job)
            new_workflow.add_job(new_job)

        command = commands.RemoveJobCommand(uow, new_job.id)
        command.execute()

        session = session_factory()
        job = session.query(Job).filter_by(id=new_job.id).first()
        assert job is None
