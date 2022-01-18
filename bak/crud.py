from sqlalchemy.orm import Session

from workflower.models.models import Job, Workflow


def get_workflow(db: Session, workflow_id: int):
    return db.query(Workflow).filter(Workflow.id == workflow_id).first()


def get_workflow_by_name(db: Session, name: str):
    return db.query(Workflow).filter(Workflow.name == name).first()


def get_workflows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Workflow).offset(skip).limit(limit).all()


def create_workflow(db: Session, workflow: Workflow):
    db_workflow = Workflow(name=workflow.name)
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Job).offset(skip).limit(limit).all()


def create_workflow_job(db: Session, job: Job, workflow_id: int):
    db_job = Job(job.id, job.name, workflow_id=workflow_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
