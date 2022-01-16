from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas
from workflower.crud import get_workflow
from workflower.db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/workflows/", response_model=schemas.Workflow)
def create_workflow(
    workflow: schemas.WorkflowCreate, db: Session = Depends(get_db)
):
    db_workflow = crud.get_workflow_by_name(db, name=workflow.name)
    if db_workflow:
        raise HTTPException(
            status_code=400, detail="workflow already registered"
        )
    return crud.create_workflow(db=db, workflow=workflow)


@app.get("/workflows/", response_model=List[schemas.Workflow])
def read_workflows(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_workflow)
):
    workflows = crud.get_workflows(db, skip=skip, limit=limit)
    return workflows


@app.get("/workflows/{workflow_id}", response_model=schemas.Workflow)
def read_workflow(workflow_id: int, db: Session = Depends(get_db)):
    db_workflow = crud.get_workflow(db, workflow_id=workflow_id)
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_workflow


@app.post("/workflows/{workflow_id}/jobs/", response_model=schemas.Job)
def create_job_for_workflow(
    workflow_id: int, job: schemas.JobCreate, db: Session = Depends(get_db)
):
    return crud.create_workflow_job(db=db, job=job, workflow_id=workflow_id)


@app.get("/jobs/", response_model=List[schemas.Job])
def read_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db, skip=skip, limit=limit)
    return jobs
