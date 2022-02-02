from workflower import core
from workflower.init_db import init_db

FUNCTION_MAP = {
    "init-db": init_db,
    "run": core.run,
}
