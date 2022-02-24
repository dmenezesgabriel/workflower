import os

import pytest
from workflower.application.workflow import commands
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class TestCreateWorkflowCommand:
    def test_create_workflow_command_executes_correctly(self, uow):
        command = commands.CreateWorkflowCommand(unit_of_work=uow, name="test")
        new_workflow = command.execute()

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

        command = commands.AddWorkflowJobCommand(
            unit_of_work=uow, workflow_id=workflow.id, job_id=job.id
        )
        command.execute()

        session = session_factory()
        assert len(session.query(Workflow).all()) == 1

        workflows = session.query(Workflow).all()
        assert workflows[0].name == "test"
        assert workflows[0].jobs[0].name == "test"
        assert workflows[0].jobs[0].operator == "python"
        assert workflows[0].jobs[0].definition == {"trigger": "date"}


class TestUpdateWorkflowFileExistsStateCommand:
    def test_update_workflow_file_exists_state_command_updates_file_exists(
        self, session_factory, workflow_file, uow
    ):
        file_path = str(workflow_file)
        new_workflow = Workflow(name="test", file_path=file_path)
        with uow:
            uow.workflows.add(new_workflow)

        command = commands.UpdateWorkflowFileExistsStateCommand(
            unit_of_work=uow, workflow_id=new_workflow.id
        )

        command.execute()
        session = session_factory()
        workflow = (
            session.query(Workflow).filter_by(id=new_workflow.id).first()
        )
        assert workflow.file_exists is True

    def test_update_workflow_file_exists_state_command_updates_file_not_exists(
        self, session_factory, uow
    ):

        new_workflow = Workflow(name="test", file_path="test.yml")
        with uow:
            uow.workflows.add(new_workflow)

        command = commands.UpdateWorkflowFileExistsStateCommand(
            unit_of_work=uow, workflow_id=new_workflow.id
        )

        command.execute()
        session = session_factory()
        workflow = (
            session.query(Workflow).filter_by(id=new_workflow.id).first()
        )
        assert workflow.file_exists is False


class TestUpdateModifiedWorkflowFileStateCommand:
    def test_update_modified_file_state_command_updates_file_last_modified_at(
        self, session_factory, workflow_file, uow
    ):
        file_path = str(workflow_file)
        new_workflow = Workflow(name="test", file_path=file_path)
        with uow:
            uow.workflows.add(new_workflow)

        command = commands.UpdateModifiedWorkflowFileStateCommand(
            unit_of_work=uow, workflow_id=new_workflow.id
        )

        command.execute()
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
        """
        modified_since_last_load should be false.
        """
        file_path = str(workflow_file)
        new_workflow = Workflow(name="test", file_path=file_path)
        with uow:
            uow.workflows.add(new_workflow)

        command = commands.UpdateModifiedWorkflowFileStateCommand(
            unit_of_work=uow, workflow_id=new_workflow.id
        )

        command.execute()
        session = session_factory()
        workflow = (
            session.query(Workflow).filter_by(id=new_workflow.id).first()
        )
        assert workflow.modified_since_last_load is False

    def test_update_modified_file_state_command_updates_modified_since_load_t(
        self, session_factory, workflow_file, uow
    ):
        """
        modified_since_last_load should be true.
        """
        file_path = str(workflow_file)
        new_workflow = Workflow(name="test", file_path=file_path)
        with uow:
            uow.workflows.add(new_workflow)

        command = commands.UpdateModifiedWorkflowFileStateCommand(
            unit_of_work=uow, workflow_id=new_workflow.id
        )

        command.execute()

        # File being modified
        with open(file_path, "a") as f:
            f.write("new line\n")

        command.execute()

        session = session_factory()
        workflow = (
            session.query(Workflow).filter_by(id=new_workflow.id).first()
        )

        assert workflow.modified_since_last_load is True


class TestLoadWorkflowFromYamlFileCommand:
    @pytest.fixture
    def workflow_file_wrong_name(self, tmpdir_factory):
        file_content = """
        version: "1.0"
        workflow:
            name: python_code_sample_interval_trigger
            jobs:
              - name: "hello_python_code"
                operator: python
                code: "print('Hello, World!')"
                trigger: interval
                minutes: 2
        """
        p = tmpdir_factory.mktemp("file").join("wrong_name.yaml")
        p.write_text(file_content, encoding="utf-8")
        return p

    @pytest.fixture
    def workflow_file_with_dependencies(self, tmpdir_factory):
        file_content = """
        version: "1.0"
        workflow:
            name: dependency_log_pattern_match
            jobs:
              - name: "first_job"
                operator: python
                code: "print('First Job!')"
                trigger: date
              - name: "second_job"
                operator: python
                code: "print('Second Job!')"
                trigger: dependency
                depends_on: first_job
                dependency_logs_pattern: "first"
                run_if_pattern_match: True

        """
        p = tmpdir_factory.mktemp("file").join(
            "dependency_log_pattern_match.yaml"
        )
        p.write_text(file_content, encoding="utf-8")
        return p

    def test_load_workflow_form_yaml_file_command_loads_workflow_correctly(
        self, session_factory, workflow_file, uow
    ):
        file_path = str(workflow_file)
        command = commands.LoadWorkflowFromYamlFileCommand(
            unit_of_work=uow, file_path=file_path
        )
        new_workflow = command.execute()

        session = session_factory()
        workflow = (
            session.query(Workflow).filter_by(id=new_workflow.id).first()
        )
        assert workflow.name == "python_code_sample_interval_trigger"

    def test_load_workflow_form_yaml_file_command_loads_workflow_fail_by_name(
        self, session_factory, workflow_file_wrong_name, uow
    ):
        file_path = str(workflow_file_wrong_name)
        command = commands.LoadWorkflowFromYamlFileCommand(
            unit_of_work=uow, file_path=file_path
        )
        workflow = command.execute()

        assert workflow is None

    def test_load_workflow_form_yaml_file_command_loads_workflow_exists_true(
        self, session_factory, workflow_file, uow
    ):
        file_path = str(workflow_file)
        new_workflow = Workflow(
            name="python_code_sample_interval_trigger", file_path=file_path
        )
        with uow:
            uow.workflows.add(new_workflow)

        command = commands.LoadWorkflowFromYamlFileCommand(
            unit_of_work=uow, file_path=file_path
        )
        workflow = command.execute()
        assert new_workflow.id == workflow.id

    def test_load_workflow_form_yaml_file_command_loads_workflow_add_jobs(
        self, session_factory, workflow_file, uow
    ):
        file_path = str(workflow_file)
        command = commands.LoadWorkflowFromYamlFileCommand(
            unit_of_work=uow, file_path=file_path
        )
        new_workflow = command.execute()

        session = session_factory()
        workflow = (
            session.query(Workflow).filter_by(id=new_workflow.id).first()
        )
        assert workflow.name == "python_code_sample_interval_trigger"
        assert workflow.jobs_count == 1
        assert workflow.jobs[0].name == "hello_python_code"
        assert workflow.jobs[0].operator == "python"

    def test_load_workflow_form_yaml_file_command_loads_workflow_add_jobs_deps(
        self, session_factory, workflow_file_with_dependencies, uow
    ):
        file_path = str(workflow_file_with_dependencies)
        command = commands.LoadWorkflowFromYamlFileCommand(
            unit_of_work=uow, file_path=file_path
        )
        new_workflow = command.execute()

        session = session_factory()
        workflow = (
            session.query(Workflow).filter_by(id=new_workflow.id).first()
        )
        assert workflow.name == "dependency_log_pattern_match"
        assert workflow.jobs_count == 2
        assert workflow.jobs[0].name == "first_job"
        assert workflow.jobs[0].operator == "python"
        assert workflow.jobs[0].depends_on is None
        assert workflow.jobs[1].name == "second_job"
        assert workflow.jobs[1].operator == "python"
        assert workflow.jobs[1].depends_on == str(workflow.jobs[0].id)

    def test_load_workflow_form_yaml_file_command_loads_workflow_job_exists(
        self, session_factory, workflow_file, uow
    ):
        new_workflow = Workflow(name="python_code_sample_interval_trigger")
        new_job = Job(
            name="hello_python_code",
            operator="python",
            definition={"trigger": "interval"},
        )

        with uow:
            uow.workflows.add(new_workflow)
            uow.jobs.add(new_job)
            new_workflow.add_job(new_job)

        file_path = str(workflow_file)
        command = commands.LoadWorkflowFromYamlFileCommand(
            unit_of_work=uow, file_path=file_path
        )
        workflow = command.execute()

        assert workflow.name == "python_code_sample_interval_trigger"
        assert workflow.jobs_count == 1
        assert workflow.jobs[0].id == new_job.id
        assert workflow.jobs[0].name == "hello_python_code"
        assert workflow.jobs[0].operator == "python"

    def test_load_workflow_form_yaml_file_command_loads_workflow_modified(
        self, session_factory, workflow_file, uow
    ):
        file_path = str(workflow_file)
        first_load_command = commands.LoadWorkflowFromYamlFileCommand(
            unit_of_work=uow, file_path=file_path
        )
        new_workflow = first_load_command.execute()

        assert new_workflow.name == "python_code_sample_interval_trigger"
        assert new_workflow.jobs_count == 1
        assert new_workflow.jobs[0].name == "hello_python_code"
        assert new_workflow.jobs[0].operator == "python"

        file_content = """
        version: "1.0"
        workflow:
            name: python_code_sample_interval_trigger
            jobs:
              - name: "first_job"
                operator: python
                code: "print('First Job!')"
                trigger: date
              - name: "second_job"
                operator: python
                code: "print('Second Job!')"
                trigger: dependency
                depends_on: first_job
                dependency_logs_pattern: "first"
                run_if_pattern_match: True

        """
        with open(file_path, "w") as f:
            f.write(file_content)

        update_state_command = commands.UpdateModifiedWorkflowFileStateCommand(
            unit_of_work=uow, workflow_id=new_workflow.id
        )
        update_state_command.execute()

        second_load_command = commands.LoadWorkflowFromYamlFileCommand(
            unit_of_work=uow, file_path=file_path
        )
        workflow = second_load_command.execute()

        session = session_factory()
        record = session.query(Workflow).filter_by(id=new_workflow.id).first()

        assert workflow.id == new_workflow.id
        assert record.id == workflow.id
        assert record.name == "python_code_sample_interval_trigger"
        assert record.jobs_count == 2
        assert record.jobs[0].name == "first_job"
        assert record.jobs[0].operator == "python"
        assert record.jobs[1].name == "second_job"
        assert record.jobs[1].operator == "python"


class TestDeactivateWorkflowJobsCommand:
    def test_deactivate_workflow_jobs_command_should_update_is_active_false(
        self, session_factory, workflow_file, uow
    ):
        file_path = str(workflow_file)
        load_command = commands.LoadWorkflowFromYamlFileCommand(
            unit_of_work=uow, file_path=file_path
        )
        new_workflow = load_command.execute()

        assert new_workflow.name == "python_code_sample_interval_trigger"
        assert new_workflow.jobs_count == 1
        assert new_workflow.jobs[0].name == "hello_python_code"
        assert new_workflow.jobs[0].operator == "python"
        assert new_workflow.jobs[0].is_active is True

        deactivate_command = commands.DeactivateWorkflowJobsCommand(
            unit_of_work=uow, workflow_id=new_workflow.id
        )
        deactivate_command.execute()

        session = session_factory()
        record = session.query(Workflow).filter_by(id=new_workflow.id).first()

        assert record.name == "python_code_sample_interval_trigger"
        assert record.jobs_count == 1
        assert record.jobs[0].name == "hello_python_code"
        assert record.jobs[0].operator == "python"
        assert record.jobs[0].is_active is False


class TestActivateWorkflowJobsCommand:
    def test_deactivate_workflow_jobs_command_should_update_is_active_false(
        self, session_factory, workflow_file, uow
    ):
        file_path = str(workflow_file)
        load_command = commands.LoadWorkflowFromYamlFileCommand(
            unit_of_work=uow, file_path=file_path
        )
        new_workflow = load_command.execute()

        assert new_workflow.name == "python_code_sample_interval_trigger"
        assert new_workflow.jobs_count == 1
        assert new_workflow.jobs[0].name == "hello_python_code"
        assert new_workflow.jobs[0].operator == "python"
        assert new_workflow.jobs[0].is_active is True

        deactivate_command = commands.DeactivateWorkflowJobsCommand(
            unit_of_work=uow, workflow_id=new_workflow.id
        )
        deactivate_command.execute()

        session = session_factory()
        record = session.query(Workflow).filter_by(id=new_workflow.id).first()

        assert record.name == "python_code_sample_interval_trigger"
        assert record.jobs_count == 1
        assert record.jobs[0].name == "hello_python_code"
        assert record.jobs[0].operator == "python"
        assert record.jobs[0].is_active is False

        activate_command = commands.ActivateWorkflowJobsCommand(
            unit_of_work=uow, workflow_id=new_workflow.id
        )
        activate_command.execute()

        new_session = session_factory()
        updated_record = (
            new_session.query(Workflow).filter_by(id=new_workflow.id).first()
        )

        assert updated_record.name == "python_code_sample_interval_trigger"
        assert updated_record.jobs_count == 1
        assert updated_record.jobs[0].name == "hello_python_code"
        assert updated_record.jobs[0].operator == "python"
        assert updated_record.jobs[0].is_active is True
