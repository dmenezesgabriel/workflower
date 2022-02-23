from workflower.domain.entities.job import Job


class TestJobEntity:
    def test_job_initialize_correclty(self):
        job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )
        assert isinstance(job, Job)
        assert job.name == "test"

    def test_job_initialize_correctly_from_dict(self):
        job_dict = dict(
            name="test",
            operator="python",
            definition=dict(trigger="date"),
        )
        job = Job.from_dict(job_dict)
        assert isinstance(job, Job)
        assert job.name == "test"
