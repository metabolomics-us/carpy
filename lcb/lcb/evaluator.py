from abc import abstractmethod
from typing import Optional

from cisclient.client import CISClient
from stasis_client.client import StasisClient

from lcb.load_secrets import Secrets


class Evaluator:
    """
    basic avaulator of command line arguments
    """

    def __init__(self, secret: Optional[Secrets] = None):
        if secret is None:
            secret = Secrets()

        self._secret = secret
        self._secret_config = secret.load()

        self.stasisClient = StasisClient(url=self._secret_config['STASIS_URL'],
                                         token=self._secret_config['STASIS_TOKEN'])
        self.cisClient = CISClient(url=self._secret_config['CIS_URL'], token=self._secret_config['CIS_TOKEN'])

    @abstractmethod
    def evaluate(self, args: dict):
        pass
