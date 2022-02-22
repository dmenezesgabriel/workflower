import logging

from workflower.config import Config

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

logger = logging.getLogger("workflower.adapters.sqlalchemy.setup")


@event.listens_for(Engine, "connect")
def connect(dbapi_con, connection_record):
    """
    Listener to make connection set WAL mode on SQLite.
    """

    # TODO
    # Verify if engine is SQlite type.

    logger.debug("Setting Wall Mode")
    cursor = dbapi_con.cursor()
    cursor.execute("pragma journal_mode=WAL")
    cursor.close()


engine = create_engine(
    Config.APP_DATABASE_URL,
    connect_args={
        "timeout": 15,
    },
    echo=True,
)

Session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
)
