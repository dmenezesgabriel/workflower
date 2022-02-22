"""
Job class.
"""

import logging

logger = logging.getLogger("workflower.job")


class Job:
    """
    Domain object for the job.

    Args:
        - name (str): Name of the given job.
        - operator (str): Operator name used by the job.
        - definition (json): Job definition that will be used by APScheduler.
        - depends_on (str, optional): Name of dependency job.
        - workflow (Workflow): Related workflow object.
        - dependency_logs_pattern (str, optional): Key word pattern to match.
        - run_if_pattern_match (bool, optional): Run or not if pattern match.
        - is_active (bool, optional): Job is active or not.
        - next_run_time (str, optional): Next job run time datetime.
    """

    def __init__(
        self,
        name,
        operator,
        definition,
        workflow,
        depends_on=None,
        dependency_logs_pattern=None,
        run_if_pattern_match=True,
        is_active=True,
        next_run_time=None,
    ):
        # TODO
        # Add state according with triggers
        # scheduled
        # running
        # executed (if trigger says tha should run only once)
        self.name = name
        self.operator = operator
        self.definition = definition
        self.depends_on = depends_on
        self.dependency_logs_pattern = dependency_logs_pattern
        self.run_if_pattern_match = run_if_pattern_match
        self.workflow = workflow
        self.is_active = is_active
        self.next_run_time = next_run_time
        self.job_scheduled_ref = None

    def __repr__(self) -> str:
        return (
            f"Job(name={self.name}, operator={self.operator}, "
            f"definition={self.definition}, "
            f"depends_on={self.depends_on}, "
            f"dependency_logs_pattern={self.dependency_logs_pattern}, "
            f"run_if_pattern_match={self.run_if_pattern_match}, "
            f"workflow={self.workflow}, "
            f"next_run_time={self.next_run_time}, "
        )
