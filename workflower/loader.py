import logging
import os
import traceback
from typing import List

from config import Config

from workflower.models.job import Job
from workflower.models.workflow import Workflow
from workflower.utils.file import yaml_file_to_dict
from workflower.utils.schema import validate_schema

logger = logging.getLogger("workflower.loader")


class Loader:
    def load_one_workflow_from_file(
        self, workflow_yaml_config_path: str
    ) -> Workflow:
        """
        Load one workflow from a yaml file.
        """
        # TODO
        # Pytest this function
        logger.info(f"Loading pipeline file: {workflow_yaml_config_path}")
        configuration_dict = yaml_file_to_dict(workflow_yaml_config_path)
        # Validate file
        validate_schema(configuration_dict)
        Workflow.from_dict(workflow_yaml_config_path, configuration_dict)
        logger.debug("Loading jobs")
        workflow_name = configuration_dict["workflow"]["name"]
        workflow_job_dicts = configuration_dict["workflow"]["jobs"]
        for workflow_job_dict in workflow_job_dicts:
            Job.from_dict(workflow_job_dict, workflow_name)

    def load_all_workflows_from_dir(
        self, workflows_path: str = Config.WORKFLOWS_FILES_PATH
    ) -> List:
        """
        Load all.
        """
        logger.info(f"Loading Workflows from directory: {workflows_path}")
        for root, dirs, files in os.walk(workflows_path):
            for file in files:
                if file.endswith(".yml") or file.endswith(".yaml"):
                    workflow_yaml_config_path = os.path.join(root, file)
                    try:
                        self.load_one_workflow_from_file(
                            workflow_yaml_config_path
                        )
                    except Exception:
                        logger.error(
                            f"Error loading {workflow_yaml_config_path}:"
                            f" {traceback.format_exc()}"
                        )
        Workflow.set_files_still_exists()

    def load_all(self):
        """
        Load workflows.
        """
        self.load_all_workflows_from_dir()
