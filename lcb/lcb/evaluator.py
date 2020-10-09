from abc import abstractmethod
from typing import Optional

from stasis_client.client import StasisClient

from lcb.load_secrets import Secrets


class Evaluator:
    """
    basic avaulator of command line arguments
    """

    def __init__(self, secret: Optional[Secrets] = None):
        if (secret is None):
            secret = Secrets()

        self._secret_config = secret.load()

        self.client = StasisClient(url=self._secret_config['STASIS_URL'], token=self._secret_config['STASIS_TOKEN'])

    @abstractmethod
    def evaluate(self, args: dict):
        pass
