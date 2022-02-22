"""
Workflow class.
import os
"""
import logging
from typing import List

from workflower.models.job import Job

logger = logging.getLogger("workflower.models.workflow")


class Workflow:
    """
    Domain object for the workflow.

    Args:
        - name (str): Name of the given workflow.
        - file_path(str, optional): Path of workflow file.
        - file_last_modified_at (int, optional): time since epoch of
        last file modification.
        - is_active (bool, optional): Workflow is active or not.
        - modified_since_last_load (bool, optional): Workflow has been modified
        since las load or not.
        - jobs (List[Job]): List of jobs for the workflow.
    """

    def __init__(
        self,
        name: str,
        is_active: bool = True,
        file_path: str = None,
        file_exists: bool = None,
        file_last_modified_at: str = None,
        modified_since_last_load: bool = False,
        jobs: List[Job] = None,
    ):
        self.name = name
        self.is_active = is_active
        self.file_path = file_path
        self.file_exists = file_exists
        self.file_last_modified_at = file_last_modified_at
        self.modified_since_last_load = modified_since_last_load
        self.jobs = jobs or []

    def __repr__(self) -> str:
        return (
            f"Workflow(name={self.name}, "
            f"is_active={self.is_active}, "
            f"file_path={self.file_path}, "
            f"file_exists={self.file_exists}, "
            f"file_last_modified_at={self.file_last_modified_at}, "
            f"modified_since_last_load={self.modified_since_last_load}, "
            f"jobs={self.jobs}, "
        )

    @classmethod
    def from_dict(cls, dictionary):
        """
        Workflow from dict.
        """
        name = dictionary["name"]
        return cls(name)

    def add_job(self, job: Job):
        """
        Add job to workflow.
        """
        self.jobs.append(job)

    def remove_job(self, job: Job):
        """
        Remove job from workflow.
        """
        self.jobs.remove(job)
