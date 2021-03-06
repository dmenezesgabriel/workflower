import logging
import os
import traceback
from typing import List

from workflower.adapters.sqlalchemy.setup import Session
from workflower.adapters.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from workflower.application.event.commands import CreateEventCommand
from workflower.application.workflow.commands import (
    ActivateWorkflowCommand,
    LoadWorkflowFromYamlFileCommand,
    SetWorkflowTriggerCommand,
)
from workflower.domain.entities.workflow import Workflow

logger = logging.getLogger("workflower.loader")


class WorkflowLoaderService:
    def __init__(self) -> None:
        self._workflows = None

    @property
    def workflows(self) -> List[Workflow]:
        return self._workflows

    def load_one_workflow_file(self, path: str, trigger: str = "on_schedule"):
        """
        Load one workflow from file.

        Args:
            - path (str): workflow file path
            - trigger (str): expects "on_schedule" or "on_demand".
        """
        session = Session()
        uow = SqlAlchemyUnitOfWork(session)
        # TODO
        #  Add strategy pattern
        command = LoadWorkflowFromYamlFileCommand(uow, path)
        workflow = None
        try:
            workflow = command.execute()
        except Exception:
            logger.error(f"Error loading {path}:" f" {traceback.format_exc()}")
            create_event_command = CreateEventCommand(
                uow,
                model="workflow",
                model_id=None,
                name="workflow_load_error",
                exception=traceback.format_exc(),
            )
            create_event_command.execute()

        if workflow:
            set_trigger_command = SetWorkflowTriggerCommand(
                uow, workflow.id, trigger
            )
            set_trigger_command.execute()
            activate_Workflow_command = ActivateWorkflowCommand(
                uow, workflow.id
            )
            activate_Workflow_command.execute()

            return workflow

    def load_all_from_dir(
        self, path: str, trigger: str = "on_schedule"
    ) -> List[Workflow]:
        """
        Load all workflow files from a given directory

        Args:
            - path (str): workflows file path
            - trigger (str): expects "on_schedule" or "on_demand".
        """

        self._workflows = []
        logger.info(f"Loading Workflows from directory: {path}")
        counter = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".yml") or file.endswith(".yaml"):
                    workflow_path = os.path.join(root, file)
                    workflow = self.load_one_workflow_file(
                        workflow_path, trigger=trigger
                    )
                    if workflow:
                        self._workflows.append(workflow)
                        counter += 1
        logger.info(f"Workflows Loaded {counter}")
        return self._workflows
