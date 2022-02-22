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
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import mapper, relationship

workflow: Table = Table(
    "workflow",
    metadata,
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
)

job: Table = Table(
    "job",
    metadata,
    Column(
        "name",
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
        ForeignKey("workflows.id"),
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
    UniqueConstraint("name", "workflow_id", name="_name_workflow_id_uc"),
    Index("name_workflow_id_idx", "name", "workflow_id"),
)

event: Table = Table(
    "event",
    metadata,
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
)


def run_mappers():
    """
    Provides mapping between db tables and domain models.
    """
    mapper(Workflow, workflow, properties={"jobs": relationship("Job")})
    mapper(
        Job,
        job,
        properties={
            "workflow": relationship("Workflow", back_populates="jobs")
        },
    )
    mapper(Event, event)
