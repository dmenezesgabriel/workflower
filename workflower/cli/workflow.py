import logging
import time

from workflower.controllers.workflow import WorkflowContoller

# from workflower.models.base import database
from workflower.models import Workflow
from workflower.models.base import database
from workflower.scheduler import SchedulerService
from workflower.utils import crud

logger = logging.getLogger("workflower.cli.workflow")


def run_workflow(path):
    scheduler_service = SchedulerService()
    workflow_controller = WorkflowContoller()
    with database.session_scope() as session:
        workflow = Workflow.from_yaml(session, path)
        crud.update(
            session, Workflow, dict(id=workflow.id), dict(is_active=True)
        )
        workflow_controller.schedule_one_workflow_jobs(
            session, workflow, scheduler_service.scheduler
        )
        scheduler_service.start()
        #  wait till trigger deps
        time.sleep(1.2)
        workflow.unschedule_jobs(scheduler_service.scheduler)
        workflow.deactivate_all_jobs(session)
