from workflower.domain.entities.event import Event


class TestEventEntity:
    def test_event_initialize_correclty(self):
        event = Event(
            name="job_added",
            model="job",
            model_id="1",
            exception=None,
            output=None,
        )
        assert isinstance(event, Event)
        assert event.name == "job_added"
        assert event.model == "job"
        assert event.model_id == "1"
        assert event.exception is None
        assert event.output is None
