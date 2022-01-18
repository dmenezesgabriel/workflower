from workflower.database import engine
from workflower.models import models

models.Base.metadata.create_all(bind=engine)
