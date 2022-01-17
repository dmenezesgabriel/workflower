"""
Workflow class.
"""


class Workflow:
    def __init__(self, name, jobs):
        self.name = name
        self.jobs = jobs

    def schedule_jobs(self, scheduler):
        for job in self.jobs:
            job.schedule_one(scheduler)
