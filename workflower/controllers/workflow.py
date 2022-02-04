import logging
import os

from workflower.loader import Loader
from workflower.models.base import database
from workflower.models.workflow import Workflow
from workflower.utils import crud

logger = logging.getLogger("workflower.controllers.workflow")


class WorkflowContoller:
    """
    Workflow Controller.
    """

    def update_workflows_files_exists_state(self, session, workflows):
        """
        Check if file exists and update state.
        """

        for workflow in workflows:
            file_exists = os.path.isfile(workflow.file_path)
            if file_exists:
                logger.debug(f"{workflow.name} file exists")
                update_dict = {"file_exists": True}
            else:
                logger.info(f"{workflow.name} file not exists")
                update_dict = {"file_exists": False}
            filter_dict = {"name": workflow.name}
            crud.update(session, Workflow, filter_dict, update_dict)

    def schedule_workflows_jobs(self, scheduler):
        """
        run Workflow Controller.
        """
        logger.info("Scheduling workflows jobs")
        workflows_loader = Loader()
        workflows_loader.load_all_workflows_from_dir()
        with database.session_scope() as session:
            workflows = crud.get_all(session, Workflow)
            self.update_workflows_files_exists_state(session, workflows)
            for workflow in workflows:
                if workflow.modified_since_last_load:
                    logger.info(
                        f"{workflow.name} file has been modified, "
                        "unscheduling jobs"
                    )
                    workflow.unschedule_jobs(scheduler)
                elif not workflow.file_exists:
                    logger.info(
                        f"{workflow.name} file has been removed, "
                        "unscheduling jobs"
                    )
                    workflow.deactivate_all_jobs(session)
                    workflow.unschedule_jobs(scheduler)
                    logger.debug(
                        f"{workflow.name} inactive is inactive, skipping"
                    )
                    crud.update(
                        session,
                        Workflow,
                        {"id": workflow.id},
                        {"is_active": False},
                    )
                    continue
                logger.info("Scheduling jobs")
                workflow.schedule_jobs(scheduler)
