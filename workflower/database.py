"""
Database class
"""
from contextlib import contextmanager

from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


class DatabaseManager:
    """
    Database application's manager class.
    """

    def __init__(
        self,
        database_uri=Config.APP_DATABASE_URL,
    ) -> None:
        self.engine = create_engine(database_uri)
        self.connection = None

    def connect(self):
        self.connection = self.engine.connect()

    @contextmanager
    def session_scope(self):
        Session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        session = Session()
        try:
            yield session
        finally:
            session.close()

    def close(self):
        self.connection.close()
