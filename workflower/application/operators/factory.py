from workflower.application.operators.alteryx import AlteryxOperator
from workflower.application.operators.module import ModuleOperator
from workflower.application.operators.operator import BaseOperator
from workflower.application.operators.papermill import PapermillOperator
from workflower.application.operators.python import PythonOperator


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
