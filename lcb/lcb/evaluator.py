from abc import abstractmethod

from stasis_client.client import StasisClient


class Evaluator:
    """
    basic avaulator of command line arguments
    """

    def __init__(self, stasis: StasisClient):
        self.client = stasis

    @abstractmethod
    def evaluate(self, args: dict):
        pass


