from workflower import models
from workflower.database import engine

models.Base.metadata.create_all(bind=engine)
