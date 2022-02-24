from workflower import core
from workflower.cli import workflow

FUNCTION_MAP = {
    "run": core.run,
    "run_workflow": workflow.run_workflow,
}
