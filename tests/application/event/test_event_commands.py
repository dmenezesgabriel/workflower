from workflower.application.event import commands


class TestCreateEventCommand:
    def test_create_workflow_command_executes_correctly(self, uow):
        command = commands.CreateEventCommand(
            uow,
            name="job_added",
            model="job",
            model_id="1",
            exception=None,
            output=None,
        )
        new_event = command.execute()

        new_event_id = new_event.id
        with uow:
            event = uow.events.get(id=new_event_id)
        assert event.name == "job_added"
        assert event.model == "job"
        assert event.model_id == "1"
