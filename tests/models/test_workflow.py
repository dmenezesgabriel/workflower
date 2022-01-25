"""
Workflow class tests.
"""

import pytest
from workflower.models.base import BaseModel, database
from workflower.models.workflow import Workflow


@pytest.fixture(scope="function")
def connection():
    database.connect()
    BaseModel.metadata.create_all(bind=database.engine)
    try:
        yield connection
    finally:
        BaseModel.metadata.drop_all(bind=database.engine)
        database.close()


def test_create_workflow(connection):
    workflow = Workflow.create(name="test")
    assert workflow.name == "test"


def test_get_one(connection):
    name = "test"
    Workflow.create(name=name)
    workflow = Workflow.get_one(name=name)
    assert workflow.name == name


def test_get_all(connection):
    names = ["test1", "test2", "test3"]
    for name in names:
        Workflow.create(name=name)
    workflows = Workflow.get_all()
    created_workflow_names = [workflow.name for workflow in workflows]
    assert all(
        [workflow_name in created_workflow_names for workflow_name in names]
    )


def test_update_(connection):
    new_name = "changed_name"
    workflow_before_update = Workflow.create(name="test")
    id = workflow_before_update.id
    Workflow.update({"id": id}, {"name": new_name})
    workflow_after_update = Workflow.get_one(id=id)
    assert workflow_after_update.name == new_name


def test_delete(connection):
    name = "changed_name"
    Workflow.create(name=name)
    Workflow.delete(name=name)
    assert Workflow.get_one(name=name) is None
