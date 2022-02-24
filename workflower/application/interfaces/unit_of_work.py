from abc import ABC, abstractclassmethod
from typing import Any


class UnitOfWork(ABC):
    """
    Port (Interface) for transaction management (usually, but not only database
    transactions).
    """

    @abstractclassmethod
    def __enter__(self):
        raise NotImplementedError

    @abstractclassmethod
    def __exit__(self, *args: Any) -> None:
        raise NotImplementedError
