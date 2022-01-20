"""
Workflow class.
"""


class WorkflowWrapper:
    def __init__(self, name, jobs, last_modified_at):
        self.name = name
        self.jobs = jobs
        self.last_modified_at = last_modified_at

    def schedule_jobs(self, scheduler):
        for job in self.jobs:
            # If job has dependencies wait till the event of
            # it's job dependency occurs
            if job.depends_on:
                continue
            job.schedule(scheduler)
