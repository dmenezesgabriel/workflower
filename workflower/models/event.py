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

    def __repr__(self) -> str:
        return (
            f"Event(name={self.name}, model={self.model}, "
            f"model_id={self.model_id}, "
            f"exception={self.exception}, "
            f"output={self.output})"
        )
