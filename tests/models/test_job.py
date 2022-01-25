import pytest
from workflower.models.base import BaseModel, database
from workflower.models.job import Job
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


@pytest.fixture(scope="function")
def workflow(connection):
    pass


def test_create():
    pass


def test_get_one():
    pass


def test_get_all():
    pass


def test_update():
    pass


def test_delete():
    pass
