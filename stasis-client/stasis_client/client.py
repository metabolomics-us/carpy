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
        """Returns the state of the given sample by calling Stasis' tracking API
        Args:
            sample_name: name of the sample

        Returns:
            the tracking object for the specified sample in json format.
            e.a.:
                "status": [
                    {
                        "time": 1530310132504,
                        "priority": 100,
                        "fileHandle": "123.d",
                        "value": "acquired"
                    }
                ]
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

    # def get_experiment(self, experiment_name, samples, start_sample=None):
    #
    #     if start_sample is None:
    #         print('getting initial page...')
    #         response = requests.get("{}/experiment/{}".format(self._url, experiment_name), headers=self._header).json()
    #         samples += response['items']
    #     else:
    #         print('getting mode pages...')
    #         response = requests.get("{}/experiment/{}/25/{}".format(self._url, experiment_name, start_sample),
    #                                 headers=self._header).json()
    #         samples += response['items']
    #
    #     if 'last_item' in response and response['last_item']:
    #         return self.get_experiment(experiment_name, samples, response['last_item']['id'])
    #
    #     return samples
