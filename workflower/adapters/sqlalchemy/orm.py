# TODO
# Clean architecture for ORM
# Refs
# - https://github.com/jorzel/opentable
# - https://github.com/pcieslinski/courses_platform
# - https://github.com/evoludigit/clean_fastapi
# - https://github.com/kurosouza/webshop
from workflower.adapters.sqlalchemy.setup import metadata
from workflower.domain.entities.event import Event
from workflower.domain.entities.job import Job
from workflower.domain.entities.workflow import Workflow

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import mapper, relationship
from sqlalchemy.sql import func

workflow: Table = Table(
    "workflow",
    metadata,
    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    ),
    Column(
        "name",
        String,
        unique=True,
        index=True,
    ),
    Column(
        "file_path",
        String,
        unique=True,
    ),
    Column(
        "trigger",
        String,
    ),
    Column(
        "file_exists",
        Boolean,
        default=True,
    ),
    Column(
        "is_active",
        Boolean,
        default=True,
    ),
    Column(
        "file_last_modified_at",
        String,
    ),
    Column(
        "modified_since_last_load",
        Boolean,
        default=False,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        onupdate=func.now(),
    ),
)

job: Table = Table(
    "job",
    metadata,
    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    ),
    Column(
        "name",
        String,
    ),
    Column(
        "status",
        String,
    ),
    Column(
        "operator",
        String,
    ),
    Column(
        "definition",
        JSON,
    ),
    Column(
        "depends_on",
        String,
    ),
    Column(
        "dependency_logs_pattern",
        String,
    ),
    Column(
        "run_if_pattern_match",
        Boolean,
        default=True,
    ),
    Column(
        "workflow_id",
        Integer,
        ForeignKey("workflow.id"),
    ),
    Column(
        "is_active",
        Boolean,
        default=True,
    ),
    Column(
        "next_run_time",
        String,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        onupdate=func.now(),
    ),
    UniqueConstraint("name", "workflow_id", name="_name_workflow_id_uc"),
    Index("name_workflow_id_idx", "name", "workflow_id"),
)

event: Table = Table(
    "event",
    metadata,
    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    ),
    Column(
        "name",
        String,
    ),
    Column(
        "model",
        String,
    ),
    Column(
        "model_id",
        String,
    ),
    Column(
        "exception",
        String,
    ),
    Column(
        "output",
        String,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        onupdate=func.now(),
    ),
)


def run_mappers():
    """
    Provides mapping between db tables and domain models.
    """
    mapper(Workflow, workflow, properties={"jobs": relationship(Job)})
    mapper(
        Job,
        job,
        properties={"workflow": relationship(Workflow, back_populates="jobs")},
    )
    mapper(Event, event)
