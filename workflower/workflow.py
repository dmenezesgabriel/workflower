"""
Workflow class.
"""


class Workflow:
    def __init__(self, name, jobs, modified_at):
        self.name = name
        self.jobs = jobs
        self.modified_at = modified_at

    def schedule_jobs(self, scheduler):
        for job in self.jobs:
            job.schedule_one(scheduler)
