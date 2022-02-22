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
        name,
        is_active=True,
        # File
        file_path=None,
        file_exists=None,
        file_last_modified_at=None,
        modified_since_last_load=False,
        #  Jobs
        jobs=None,
    ):
        self.name = name
        self.file_path = file_path
        self.file_exists = file_exists
        self.file_last_modified_at = file_last_modified_at
        self.modified_since_last_load = modified_since_last_load
        self.is_active = is_active
        self.jobs: List[Job] or None = jobs

    def __repr__(self) -> str:
        return (
            f"Workflow(name={self.name}, file_path={self.file_path}, "
            f"file_last_modified_at={self.file_last_modified_at}, "
            f"modified_since_last_load={self.modified_since_last_load}, "
            f"is_active={self.is_active}"
        )

    @classmethod
    def from_dict(cls, dictionary):
        """
        Workflow from dict.
        """
        return cls(dictionary["name"])
