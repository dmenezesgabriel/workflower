import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from workflower.config import Config
from workflower.loader import WorkflowLoader
from workflower.models import Workflow
from workflower.models.base import BaseModel


@pytest.fixture(scope="function")
def session():
    """
    sqlalchemy.orm.session.Session.
    """
    engine = create_engine(Config.APP_DATABASE_URL)
    BaseModel.metadata.create_all(bind=engine)
    Session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()
        BaseModel.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def temp_workflow_file(tmpdir_factory):
    file_content = """
    version: "1.0"
    workflow:
        name: test_file
        jobs:
          - name: "hello_python_code"
            uses: python
            code: "print('Hello, World!')"
            trigger: interval
            minutes: 2
    """
    p = tmpdir_factory.mktemp("file").join("test_file.yaml")
    p.write_text(file_content, encoding="utf-8")
    return p


class TestWorkflowLoader:
    def test_load_one(cls, session, temp_workflow_file):
        workflow_loader = WorkflowLoader()
        print(temp_workflow_file.basename)
        workflow = workflow_loader.load_one_from_file(
            session, str(temp_workflow_file)
        )
        assert isinstance(workflow, Workflow)
