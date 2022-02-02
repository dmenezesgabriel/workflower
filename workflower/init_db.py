import logging
import os

from workflower.config import Config
from workflower.models.base import BaseModel, database

# Models must be imported even if unused so the tables can be declared.
from workflower.models.event import Event
from workflower.models.job import Job
from workflower.models.workflow import Workflow

sqlalchemy_logger = logging.getLogger("sqlalchemy")
sqlalchemy_logger.setLevel(logging.DEBUG)

logger = logging.getLogger("Init_db")
logger.setLevel(logging.INFO)


def init_db():
    if not os.path.isdir(Config.DATA_DIR):
        os.makedirs(Config.DATA_DIR)
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
