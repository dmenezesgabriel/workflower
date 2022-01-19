"""
Workflower Models
"""
from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    jobs = relationship("Job", back_populates="workflow")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    definition = Column(JSON, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))

    workflow = relationship("Workflow", back_populates="jobs")


class Event(Base):
    """
    TODO
    https://apscheduler.readthedocs.io/en/3.x/modules/events.html?highlight=events#apscheduler.events.JobEvent
    """

    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String)  # Executor, Job, Jobstore, Workflow
    model_id = Column(String)
    name = Column(String)
