import os
from typing import Optional

import boto3
import boto3.s3
import requests
import simplejson as json
from botocore.exceptions import ClientError
from simplejson import JSONDecodeError


class StasisClient:
    """
    a simple client to interact with the stasis system in a safe and secure manner.
    """

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None, test: Optional[bool] = False):
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
            self._token = os.getenv('STASIS_API_TOKEN') if test else os.getenv('PROD_STASIS_API_TOKEN')
        if self._url is None:
            self._url = os.getenv('STASIS_URL')

        self._header = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': f'{self._token}'
        }
        print(f'HEADER: {self._header}')


        bucket_name = f'wcmc-data-stasis-result-{"test" if test else "prod"}'
        if boto3.client('s3').head_bucket(Bucket=bucket_name):
            self.bucket = boto3.resource('s3').Bucket(bucket_name)

    def sample_acquisition_create(self, data: dict):
        """
        updloads the
        :param data: the data object containing the aquisiton description
        :return:
        """
        return requests.post(f'{self._url}/acquisition', json=data, headers=self._header)

    def sample_acquisition_get(self, sample_name):
        """
        returns the acquistion data of this sample

        :param sample_name:
        :return:
        """
        return requests.get(f'{self._url}/acquisition/{sample_name}', headers=self._header).json()

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

    def sample_result(self, sample_name: str, dest: Optional[str] = 'tmp') -> dict:
        """
        returns the result for a specified sample
        :param sample_name:
        :return: a json object containing the result data
        """

        if not os.path.exists(dest):
            os.makedirs(dest)

        try:
            with open(f'{dest}/{sample_name}', 'wb') as data:
                self.bucket.download_fileobj(sample_name, data)

            with open(f'{dest}/{sample_name}', 'rb') as data:
                jstr = json.load(data)

            return jstr
        except JSONDecodeError as jde:
            print(f'Error deserializing json data. {jde.msg}')
            return {'Error': jde.msg}
        except ClientError as ce:
            print(f'Error getting sample results {ce.response}')
            return ce.response
        finally:
            # only remove downloads in ./tmp
            if os.path.exists(f'tmp/{sample_name}'):
                os.remove(f'tmp/{sample_name}')
