import os
from typing import Optional
import requests


class StasisClient:
    """
    a simple client to interact with the stasis system in a safe and secure manner.
    """

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        """
        the client requires an url where to connect against
        and the related token.

        :param url:
        :param token:
        """

        self._url = url
        self._token = token

        if self._token is None:
            # utilize env
            self._token = os.environ.get("STASIS_KEY")
        if self._url is None:
            self._url = os.environ.get("STASIS_URL")

        self._header = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': '{}'.format(self._token)
        }

    def sample_acquisition_create(self, data: dict):
        """
        updloads the
        :param data: the data object containing the aquisiton description
        :return:
        """
        return requests.post("{}/acquisition/".format(self._url), json=data, headers=self._header)

    def sample_acquisition_get(self, sample_name):
        """
        returns the acquistion data of this sample

        :param sample_name:
        :return:
        """
        return requests.get("{}/acquisition/{}".format(self._url, sample_name), headers=self._header).json()

    def sample_state(self, sample_name: str):
        """
        returns the state of the given sample
        :param sample_name:
        :return:
        """
        return requests.get("{}/tracking/{}".format(self._url, sample_name), headers=self._header).json()['status']

    def sample_state_update(self, sample_name: str, state):
        """
        updates a sample state in the remote system+
        :param sample_name:
        :param state:
        :return:
        """
        data = {
            "sample": sample_name,
            "status": state
        }
        return requests.post("{}/tracking".format(self._url), json=data, headers=self._header)

    def sample_result(self, sample_name: str) -> dict:
        """
        returns the result for a specified sample
        :param sample_name:
        :return:
        """
        return requests.get("{}/result/{}".format(self._url, sample_name), headers=self._header).json()

