from typing import List

import yaml
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow


class SchemaBuilder:
    def create_workflow(self, **kwargs):
        return Workflow(**kwargs)

    def create_job(self, **kwargs):
        return Job(**kwargs)

    def build(self, path: str, workflow: Workflow, jobs: List[Job]):
        for job in jobs:
            workflow.add_job(job)
        workflow_dictionary = workflow.to_dict()
        with open(path, "w") as file:
            yaml.dump(workflow_dictionary, file)
