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
