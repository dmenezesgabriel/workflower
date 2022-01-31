"""
Database class
"""
import logging
from contextlib import contextmanager

from config import Config
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

logger = logging.getLogger("workflower.database")


@event.listens_for(Engine, "connect")
def connect(dbapi_con, connection_record):
    logger.debug("Setting Wall Mode")
    cursor = dbapi_con.cursor()
    cursor.execute("pragma journal_mode=WAL")
    cursor.close()


class DatabaseManager:
    """
    Database application's manager class.
    """

    def __init__(
        self,
        database_uri=Config.APP_DATABASE_URL,
        timeout=10,
    ) -> None:
        self.engine = create_engine(
            database_uri,
            connect_args={
                "timeout": timeout,
            },
        )
        self.connection = None

    def connect(self):
        self.connection = self.engine.connect()

    @contextmanager
    def session_scope(self):
        Session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
            )
        )
        session = Session()
        try:
            yield session
        finally:
            session.close()

    def close(self):
        self.connection.close()
