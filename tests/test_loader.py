import pandas as pd
import pytest
from workflower.loader import Loader
from workflower.models.base import BaseModel, database

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)


@pytest.fixture(scope="function")
def connection():
    database.connect()
    BaseModel.metadata.create_all(bind=database.engine)
    try:
        yield connection
    finally:
        BaseModel.metadata.drop_all(bind=database.engine)
        database.close()


def test_load_one_workflow_from_file(connection):
    loader = Loader()
    loader.load_one_workflow_from_file(
        "tests/resources/papermill_sample_cron_trigger_with_deps.yml"
    )

    df = pd.read_sql("select * from workflows", database.engine)
    assert df.name.to_list()[0] == "papermill_sample_cron_trigger_with_deps"
    df = pd.read_sql("select * from jobs", database.engine)
    assert len(df) == 2
