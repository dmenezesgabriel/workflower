"""
Workflow class tests.
"""

import pytest
from workflower.models.base import BaseModel, database
from workflower.models.workflow import Workflow


@pytest.fixture(scope="function")
def connection():
    """
    Establish connection with tests database.
    """
    database.connect()
    BaseModel.metadata.create_all(bind=database.engine)
    try:
        yield connection
    finally:
        BaseModel.metadata.drop_all(bind=database.engine)
        database.close()


def test_create(connection):
    """
    Should create object with name test.
    """

    workflow = Workflow.create(name="test")
    assert workflow.name == "test"


def test_get_one(connection):
    """
    Should return created object.
    """
    # Definition
    name = "test"
    # Preparing
    Workflow.create(name=name)
    workflow = Workflow.get_one(name=name)
    # Testing
    assert workflow.name == name


def test_get_all(connection):
    """
    Should return all created objects.
    """
    # Definitions
    names = ["test1", "test2", "test3"]
    # Preparing
    for name in names:
        Workflow.create(name=name)
    workflows = Workflow.get_all()
    created_workflow_names = [workflow.name for workflow in workflows]
    # Testing
    assert all(
        [workflow_name in created_workflow_names for workflow_name in names]
    )


def test_update_(connection):
    """
    Should update object attributes.
    """

    # Definitions
    new_name = "changed_name"
    # Preparing
    workflow_before_update = Workflow.create(name="test")
    id = workflow_before_update.id
    Workflow.update({"id": id}, {"name": new_name})
    workflow_after_update = Workflow.get_one(id=id)
    # Testing
    assert workflow_after_update.name == new_name


def test_delete(connection):
    """
    Should delete object.
    """

    # Definitions
    name = "changed_name"
    # Preparing
    Workflow.create(name=name)
    Workflow.delete(name=name)
    # Testing
    assert Workflow.get_one(name=name) is None


def test_from_dict(connection):
    """
    Should create object from dict and yaml file path.
    """

    # Definitions
    name = "papermill_sample_cron_trigger_with_deps"
    workflow_yaml_config_path = (
        "tests/resources/papermill_sample_cron_trigger_with_deps.yml"
    )
    configuration_dict = {
        "version": 1.0,
        "workflow": {
            "name": name,
            "jobs": [],
        },
    }
    # Preparing
    Workflow.from_dict(workflow_yaml_config_path, configuration_dict)
    workflow = Workflow.get_one(name=name)
    # Testing
    assert workflow.name == name
