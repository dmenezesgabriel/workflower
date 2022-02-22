import logging
import os
import traceback
from abc import ABC, abstractclassmethod
from typing import List

from workflower.config import Config
from workflower.domain.entities.workflow import Workflow
from workflower.schema.parser import WorkflowSchemaParser
from workflower.utils.file import yaml_file_to_dict

logger = logging.getLogger("workflower.loader")


class LoadStrategy(ABC):
    @abstractclassmethod
    def load(self):
        raise NotImplementedError


class YmlLoadStrategy(LoadStrategy):
    def load(self, file_path: str):
        return yaml_file_to_dict(file_path)


class WorkflowFileLoader:
    def __init__(self, strategy: LoadStrategy):
        self._strategy = strategy

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: LoadStrategy):
        self._strategy = strategy

    def load_workflow(self, file_path: str):
        WorkflowSchemaParser()
        self._strategy.load(file_path)


class WorkflowLoader:
    def __init__(self) -> None:
        self._workflows = None

    @property
    def workflows(self) -> List[Workflow]:
        return self._workflows

    def load_one_from_file(
        self, session, workflow_yaml_config_path: str
    ) -> Workflow:
        """
        Load one workflow from a yaml file.
        """
        logger.info(f"Loading pipeline file: {workflow_yaml_config_path}")
        return Workflow.from_yaml(session, workflow_yaml_config_path)

    def load_all_from_dir(
        self, session, workflows_path: str = Config.WORKFLOWS_FILES_PATH
    ) -> List[Workflow]:
        """
        Load all.
        """
        self._workflows = []
        logger.info(f"Loading Workflows from directory: {workflows_path}")
        counter = 0
        for root, dirs, files in os.walk(workflows_path):
            for file in files:
                if file.endswith(".yml") or file.endswith(".yaml"):
                    workflow_yaml_config_path = os.path.join(root, file)
                    try:
                        workflow = self.load_one_from_file(
                            session, workflow_yaml_config_path
                        )
                        counter += 1
                        if workflow:
                            self._workflows.append(workflow)
                    except Exception:
                        logger.error(
                            f"Error loading {workflow_yaml_config_path}:"
                            f" {traceback.format_exc()}"
                        )
        logger.info(f"Workflows Loaded {counter}")
        return self._workflows
