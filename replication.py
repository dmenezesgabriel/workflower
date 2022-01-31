from workflower.models.base import BaseModel, DatabaseManager, database

replica_db = DatabaseManager(database_uri="sqlite:///replica-dev.sqlite")
replica_db.connect()

try:
    BaseModel.metadata.create_all(bind=replica_db)
except Exception as error:
    print(error)

database.connect()
database.engine.execute("ATTACH DATABASE 'replica-dev.sqlite' as replica")

# import sqlite3

# replica_db = sqlite3.connect("file::memory:?cache=shared", uri=True)
# # main_db = sqlite3.connect("app-dev.sqlite", uri=True)
# replica_db.execute("ATTACH DATABASE 'app-dev.sqlite' AS master")
# print(list(replica_db.execute("select * from master.jobs")))
