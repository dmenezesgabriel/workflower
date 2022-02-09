"""
Database initialization script.

Technical debit, must be replaced with alembic migrations.
"""
import logging
import os

from workflower.config import Config
from workflower.database import DatabaseManager
from workflower.models.base import BaseModel, database

# Models must be imported even if unused so the tables can be declared.
from workflower.models.event import Event
from workflower.models.job import Job
from workflower.models.workflow import Workflow

sqlalchemy_logger = logging.getLogger("sqlalchemy")
sqlalchemy_logger.setLevel(logging.DEBUG)

logger = logging.getLogger("Init_db")
logger.setLevel(logging.INFO)


def init_db(
    database: DatabaseManager = database,
    data_dir=Config.DATA_DIR,
    create_data_directory=True,
):
    """
    Create database tables.
    """
    if create_data_directory:
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
    database.connect()
    logger.debug(f"Using engine: {database.engine}")

    try:
        with database.session_scope() as session:
            print(BaseModel.metadata.tables)

            BaseModel.metadata.create_all(bind=database.engine)
            session.commit()
    except Exception as error:
        print(error)
    finally:
        database.close()
