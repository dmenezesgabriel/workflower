import pytest
from workflower.domain.entities.event import Event
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


@pytest.fixture
def workflow_factory():
    def _workflow_factory(
        name,
        file_path,
        file_exists,
        file_last_modified_at,
        is_active,
        modified_since_last_load,
        jobs,
    ):
        return Workflow(
            name,
            file_path,
            file_exists,
            file_last_modified_at,
            is_active,
            modified_since_last_load,
            jobs,
        )

    yield _workflow_factory


@pytest.fixture
def job_factory():
    def _job_factory(
        name,
        operator,
        definition,
        depends_on,
        workflow_dependency_logs_pattern,
        run_if_pattern_match,
        is_active,
        next_run_time,
    ):
        return Job(
            name,
            operator,
            definition,
            depends_on,
            workflow_dependency_logs_pattern,
            run_if_pattern_match,
            is_active,
            next_run_time,
        )

    yield _job_factory


@pytest.fixture
def event_factory():
    def _event_factory(name, model, model_id, exception, output):
        return Event(name, model, model_id, exception, output)

    yield _event_factory
