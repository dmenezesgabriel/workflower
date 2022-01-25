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


def test_update_workflow(connection):
    new_name = "changed_name"
    workflow_before_update = Workflow.create(name="test")
    id = workflow_before_update.id
    Workflow.update({"id": id}, {"name": new_name})
    workflow_after_update = Workflow.get_one(id=id)
    assert workflow_after_update.name == new_name
