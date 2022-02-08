"""
Alteryx helper module
"""
import importlib
import importlib.util
import logging

from workflower.operators.operator import BaseOperator


class ModuleOperator(BaseOperator):
    @classmethod
    def execute(
        cls,
        module_name: str,
        module_path: str,
        *args,
        **kwargs,
    ) -> None:
        logger = logging.getLogger("workflower.operators.module")
        logger.info(f"Loading module {module_name} from path {module_path}")
        spec = importlib.util.spec_from_file_location(
            module_name,
            module_path,
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module_instance = module.Module()
        logger.info(f"Running Module {module_name}")
        module_instance.run()
