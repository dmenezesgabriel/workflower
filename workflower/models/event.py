from sqlalchemy import Column, String
from workflower.models.base import BaseModel


class Event(BaseModel):
    __tablename__ = "events"
    name = Column(
        "name",
        String,
    )
    model = Column(
        "model",
        String,
    )
    model_id = Column(
        "model_id",
        String,
    )
    exception = Column(
        "exception",
        String,
    )
    output = Column(
        "output",
        String,
    )
