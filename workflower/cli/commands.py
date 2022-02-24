from workflower import core
from workflower.adapters.sqlalchemy.setup import engine, metadata
from workflower.cli import workflow


def create_db():
    metadata.create_all(bind=engine)


FUNCTION_MAP = {
    "run": core.run,
    "init-db": create_db,
    "run_workflow": workflow.run_workflow,
}
