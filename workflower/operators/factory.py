from workflower.operators.alteryx import AlteryxOperator
from workflower.operators.module import ModuleOperator
from workflower.operators.papermill import PapermillOperator
from workflower.operators.python import PythonOperator


def create_operator(uses):
    """
    Operator Factory.
    """

    operators = {
        "alteryx": AlteryxOperator,
        "papermill": PapermillOperator,
        "python": PythonOperator,
        "module": ModuleOperator,
    }
    return operators[uses]
