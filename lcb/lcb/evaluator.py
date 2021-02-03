from abc import abstractmethod

from cisclient.client import CISClient
from stasis_client.client import StasisClient

from lcb.load_secrets import Secrets


class Evaluator:
    """
    basic avaulator of command line arguments
    """

    def evaluate_command(self, secret: Secrets, args):
        self._secret = secret
        self._secret_config = secret.load()

        self.stasisClient = StasisClient(url=self._secret_config['STASIS_URL'],
                                         token=self._secret_config['STASIS_TOKEN'])
        self.cisClient = CISClient(url=self._secret_config['CIS_URL'], token=self._secret_config['CIS_TOKEN'])

        self.evaluate(args)

    @abstractmethod
    def evaluate(self, args: dict):
        pass
