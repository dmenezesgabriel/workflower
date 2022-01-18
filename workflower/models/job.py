"""
Job class.
"""

import logging

from apscheduler.jobstores.base import ConflictingIdError

logger = logging.getLogger("workflower.job")


class JobWrapper:
    def __init__(self, name, uses=None, definition=None):
        self.name = name
        self.uses = uses
        self.definition = definition

    def schedule(self, scheduler) -> None:
        """
        Schedule a job in apscheduler
        """
        job_id = self.definition["id"]
        logger.debug(f"scheduling {job_id}")
        # TODO
        # Move to another function
        # Update job if yaml file has been modified
        logger.debug(self.definition)
        try:
            scheduler.add_job(**self.definition)
        except ConflictingIdError:
            logger.warning(f"{job_id}, already scheduled")
