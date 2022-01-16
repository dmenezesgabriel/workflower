from sqlalchemy.orm import Session

import models
import schemas


def get_workflow(db: Session, workflow_id: int):
    return (
        db.query(models.Workflow)
        .filter(models.Workflow.id == workflow_id)
        .first()
    )


def get_workflows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Workflow).offset(skip).limit(limit).all()


def create_workflow(db: Session, workflow: schemas.UserCreate):
    db_workflow = models.Workflow(name=workflow.name)
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Job).offset(skip).limit(limit).all()


def create_workflow_job(db: Session, job: schemas.JobCreate, workflow_id: int):
    db_job = models.Job(**job.dict(), workflow_id=workflow_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
