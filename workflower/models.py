"""
Workflower Models
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from workflower.database import Base

# TODO
# - Workflow Model
# - Job Model


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
    workflow_id = Column(Integer, ForeignKey("workflows.id"))

    workflow = relationship("Workflow", back_populates="jobs")
