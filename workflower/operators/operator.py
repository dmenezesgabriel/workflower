from abc import ABC, abstractclassmethod


class BaseOperator(ABC):
    """
    Operator Base class.
    """

    @abstractclassmethod
    def execute(*args, **kwargs):
        pass

    pass
