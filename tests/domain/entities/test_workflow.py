from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class TestWorkflowEntity:
    def test_workflow_initialize_correclty(self):
        workflow = Workflow(name="test")
        assert isinstance(workflow, Workflow)
        assert workflow.name == "test"

    def test_workflow_initialize_correctly_from_dict(self):
        workflow_dict = dict(name="test")
        workflow = Workflow.from_dict(workflow_dict)
        assert isinstance(workflow, Workflow)
        assert workflow.name == "test"

    def test_jobs_count_property_retuns_number_of_jobs(self):
        workflow = Workflow(
            name="test",
            jobs=[
                Job(
                    name="test",
                    operator="python",
                    definition={"trigger": "date"},
                )
            ],
        )

        assert workflow.jobs_count == 1

    def test_add_job_method_add_job_to_workflow(self):
        workflow = Workflow(name="test")
        job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )

        workflow.add_job(job)
        assert workflow.jobs[0].operator == "python"

    def test_workflow_remove_job_method_removes_job(self):
        workflow = Workflow(name="test")
        job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )
        workflow.add_job(job)
        assert workflow.jobs[0].operator == "python"
        workflow.remove_job(job)
        workflow.jobs == []

    def test_workflow_has_job_check_if_workflow_has_job(self):
        workflow = Workflow(name="test")
        job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )

        workflow.add_job(job)
        assert workflow.has_job(job)

    def test_workflow_clear_jobs_remove_all_jobs(self):
        workflow = Workflow(
            name="test",
            jobs=[
                Job(
                    name="test",
                    operator="python",
                    definition={"trigger": "date"},
                )
            ],
        )
        assert workflow.jobs[0].operator == "python"
        workflow.clear_jobs()
        workflow.jobs == []

    def test_workflow_to_dict_return_a_dict(self):
        workflow = Workflow(name="test")
        workflow_dict = workflow.to_dict()

        assert isinstance(workflow_dict, dict)
        assert workflow_dict["name"] == "test"
        assert isinstance(workflow_dict["jobs"], list)
        assert not workflow_dict["jobs"]

        job = Job(
            name="test",
            operator="python",
            definition={"trigger": "date"},
        )
        workflow.add_job(job)
        workflow_dict = workflow.to_dict()

        assert len(workflow_dict["jobs"]) == 1
