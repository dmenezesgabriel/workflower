import logging
import os
import traceback
from typing import List

from workflower.adapters.sqlalchemy.setup import Session
from workflower.adapters.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from workflower.application.workflow.commands import (
    LoadWorkflowFromYamlFileCommand,
    SetWorkflowTriggerCommand,
)
from workflower.config import Config
from workflower.domain.entities.workflow import Workflow

logger = logging.getLogger("workflower.loader")


class WorkflowLoaderService:
    def __init__(self) -> None:
        self._workflows = None

    @property
    def workflows(self) -> List[Workflow]:
        return self._workflows

    def load_all_from_dir(
        self, workflows_path: str = Config.WORKFLOWS_FILES_PATH
    ) -> List[Workflow]:
        """
        Load all.
        """
        session = Session()
        uow = SqlAlchemyUnitOfWork(session)
        self._workflows = []
        logger.info(f"Loading Workflows from directory: {workflows_path}")
        counter = 0
        for root, dirs, files in os.walk(workflows_path):
            for file in files:
                if file.endswith(".yml") or file.endswith(".yaml"):
                    file_path = os.path.join(root, file)
                    command = LoadWorkflowFromYamlFileCommand(uow, file_path)

                    try:
                        workflow = command.execute()
                        if workflow:
                            set_trigger_command = SetWorkflowTriggerCommand(
                                uow, workflow.id, "on_schedule"
                            )
                            set_trigger_command.execute()
                            counter += 1
                            self._workflows.append(workflow)
                    except Exception:
                        logger.error(
                            f"Error loading {file_path}:"
                            f" {traceback.format_exc()}"
                        )
        logger.info(f"Workflows Loaded {counter}")
        return self._workflows
