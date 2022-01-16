from typing import List

from pydantic import BaseModel


class JobBase(BaseModel):
    name: str


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int
    workflow_id: int

    class Config:
        orm_mode = True


class WorkflowBase(BaseModel):
    name: str


class WorkflowCreate(WorkflowBase):
    pass


class Workflow(WorkflowBase):
    id: int
    is_active: bool
    jobs: List[Job] = []

    class Config:
        orm_mode = True
