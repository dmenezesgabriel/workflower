"""
Workflow class.
"""


class Workflow:
    def __init__(self, name, jobs, last_modified_at):
        self.name = name
        self.jobs = jobs
        self.last_modified_at = last_modified_at

    def schedule_jobs(self, scheduler):
        for job in self.jobs:
            job.schedule(scheduler)
