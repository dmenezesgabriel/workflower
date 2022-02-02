import logging
import os

from config import Config
from workflower.models.base import BaseModel, database
from workflower.models.event import Event
from workflower.models.job import Job
from workflower.models.workflow import Workflow

logger = logging.getLogger("sqlalchemy")
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":

    if not os.path.isdir(Config.DATA_DIR):
        os.makedirs(Config.DATA_DIR)
    database.connect()
    print(database.engine)

    try:
        with database.session_scope() as session:
            print(BaseModel.metadata.tables)

            BaseModel.metadata.create_all(bind=database.engine)
            session.commit()
    except Exception as error:
        print(error)
    finally:
        database.close()
