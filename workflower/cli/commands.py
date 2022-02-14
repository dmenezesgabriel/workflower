from workflower import core
from workflower.cli import workflow
from workflower.init_db import init_db

FUNCTION_MAP = {
    "init-db": init_db,
    "run": core.run,
    "run_workflow": workflow.run_workflow,
}
