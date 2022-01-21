from workflower.models.base import BaseModel, database

if __name__ == "__main__":
    database.connect()

    try:
        BaseModel.metadata.create_all(bind=database.engine)
    except Exception as error:
        print(error)
    finally:
        database.close()
