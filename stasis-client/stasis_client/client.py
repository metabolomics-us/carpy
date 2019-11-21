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

        Args:
            url:
            token:
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

        bucket_name = f'wcmc-data-stasis-result-{"test" if test else "prod"}'
        if boto3.client('s3').head_bucket(Bucket=bucket_name):
            self.bucket = boto3.resource('s3').Bucket(bucket_name)

    def sample_acquisition_create(self, data: dict):
        """
        adds sample metadata info to stasis
        Args:
             data: the data object containing the aquisiton description
        Returns:
        """
        return requests.post(f'{self._url}/acquisition', json=data, headers=self._header)

    def sample_acquisition_get(self, sample_name):
        """
        returns the acquistion data of this sample

        Args:
             sample_name:

        Returns:
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
        return requests.get(f'{self._url}/tracking/{sample_name}', headers=self._header).json()['status']

    def sample_state_update(self, sample_name: str, state):
        """
        updates a sample state in the remote system+

        Args:
            sample_name:
            state:

        Returns:
        """
        data = {
            "sample": sample_name,
            "status": state
        }
        return requests.post(f'{self._url}/tracking', json=data, headers=self._header)

    def sample_result(self, sample_name: str, dest: Optional[str] = 'tmp') -> dict:
        """
        Downloads a sample's result

        Args:
            sample_name: filename to download
            dest: Optional folder to store the file

        Returns:
            a json object with the result data or error information
        """

        if not os.path.exists(dest):
            os.makedirs(dest)

        filename = f'{dest}/{sample_name}'

        try:
            with open(filename, 'wb') as data:
                self.bucket.download_fileobj(sample_name, data)

            with open(filename, 'rb') as data:
                jstr = json.load(data)

            return jstr
        except JSONDecodeError as jde:
            return {'Error': jde.msg, 'filename': sample_name}
        except ClientError as ce:
            return {'Error': ce.response['Error'], 'filename': sample_name}
        finally:
            # only remove downloads in ./tmp
            if os.path.exists(f'tmp/{sample_name}'):
                os.remove(f'tmp/{sample_name}')

            # or empty files
            if os.path.getsize(filename) <= 0:
                os.remove(filename)
