from workflower.operators.alteryx import AlteryxOperator
from workflower.operators.module import ModuleOperator
from workflower.operators.operator import BaseOperator
from workflower.operators.papermill import PapermillOperator
from workflower.operators.python import PythonOperator


def create_operator(operator_name: str) -> BaseOperator:
    """
    Operator Factory.
    """

    operators = {
        "alteryx": AlteryxOperator,
        "papermill": PapermillOperator,
        "python": PythonOperator,
        "module": ModuleOperator,
    }
    return operators[operator_name]
