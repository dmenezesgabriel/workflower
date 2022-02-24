from workflower.application.job import commands


class TestCreateJobCommand:
    def test_create_workflow_command_executes_correctly(self, uow):
        command = commands.CreateJobCommand(unit_of_work=uow)
        new_job = command.execute(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )

        new_job_id = new_job.id
        with uow:
            job = uow.jobs.get(id=new_job_id)
        assert job.name == "test"
        assert job.operator == "python"
