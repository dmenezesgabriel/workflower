"""
Database class
"""
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# TODO
# Database manager
# WAL Config
#  Singleton pattern

engine = create_engine(
    Config.WORKFLOWS_EXECUTION_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
