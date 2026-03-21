from abc import abstractmethod

from ...core.matches import BaseMatch

class BaseMatchAdapter:

    @abstractmethod
    def to_internal_match(self) -> BaseMatch:
        """convert the model as we got from the API to our representation of a game"""
        raise NotImplementedError()
