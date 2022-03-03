from workflower.domain.entities.job import Job


class TestJobEntity:
    def test_job_initialize_correctly(self):
        job = Job(
            name="test",
            operator="python",
            definition=dict(trigger="date", code="print('First Job!')"),
        )

        assert isinstance(job, Job)
        assert job.name == "test"
        assert job.operator == "python"
        assert job.status == "pending"

    def test_job_initialize_correctly_from_dict(self):
        job_dict = dict(
            name="test",
            operator="python",
            definition=dict(trigger="date", code="print('First Job!')"),
        )
        job = Job.from_dict(job_dict)

        assert isinstance(job, Job)
        assert job.name == "test"
        assert job.operator == "python"
        assert job.status == "pending"

    def test_job_to_dict_returns_dict(self):
        job = Job(
            name="test",
            operator="python",
            definition=dict(trigger="date", code="print('First Job!')"),
        )

        job_dict = job.to_dict()

        assert isinstance(job_dict, dict)
        assert job_dict["name"] == "test"
        assert job_dict["operator"] == "python"
        assert job_dict["trigger"] == "date"
        assert job_dict["code"] == "print('First Job!')"
