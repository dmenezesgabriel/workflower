import logging
import os
import traceback
from typing import List

from workflower.config import Config
from workflower.models.workflow import Workflow

logger = logging.getLogger("workflower.loader")


class Loader:
    def load_one_workflow_from_file(self, workflow_yaml_config_path: str):
        """
        Load one workflow from a yaml file.
        """
        logger.info(f"Loading pipeline file: {workflow_yaml_config_path}")
        Workflow.from_yaml(workflow_yaml_config_path)

    def load_all_workflows_from_dir(
        self, workflows_path: str = Config.WORKFLOWS_FILES_PATH
    ) -> None:
        """
        Load all.
        """
        logger.info(f"Loading Workflows from directory: {workflows_path}")
        counter = 0
        for root, dirs, files in os.walk(workflows_path):
            for file in files:
                if file.endswith(".yml") or file.endswith(".yaml"):
                    workflow_yaml_config_path = os.path.join(root, file)
                    try:
                        self.load_one_workflow_from_file(
                            workflow_yaml_config_path
                        )
                        counter += 1
                    except Exception:
                        logger.error(
                            f"Error loading {workflow_yaml_config_path}:"
                            f" {traceback.format_exc()}"
                        )
        logger.info(f"Workflows Loaded {counter}")
