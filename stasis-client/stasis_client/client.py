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

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
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
            self._token = os.getenv('STASIS_API_TOKEN', os.getenv('PROD_STASIS_API_TOKEN'))
        if self._url is None:
            self._url = os.getenv('STASIS_API_URL', 'https://api.metabolomics.us/stasis')

        if self._token is None:
            raise Exception("you need to to provide a stasis api token in the env variable 'STASIS_API_TOKEN'")

        if self._url is None:
            raise Exception("you need to provide a url in the env variable 'STASIS_API_URL'")

        self._header = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': f'{self._token}'
        }

    def schedule_sample_for_computation(self, sample_name: str, env: str, method: str, profile: str,
                                        resource: str = "FARGATE"):
        """
        schedules a sample for dataprocessing
        """
        result = requests.post(f"{self._url}/schedule",
                               json={'sample': sample_name, 'env': env, 'method': method, 'profile': profile,
                                     'resource': resource, 'secured': True}, headers=self._header)

        if result.status_code != 200:
            raise Exception("scheduling failed!")
        else:
            return result.json()

    def sample_raw_data_exists(self, sample_name) -> bool:
        """
        checks if the raw data exist
        """
        result = requests.head(f"{self._url}/sample/{sample_name}")

        if result.status_code == 200:
            return True
        elif result.status_code == 404:
            return False
        else:
            raise Exception("error checkign state, status code was {}".format(result.status_code))

    def sample_acquisition_create(self, data: dict):
        """
        adds sample metadata info to stasis
        Args:
             data: the data object containing the aquisiton description
        Returns:
        """
        result = requests.post(f'{self._url}/acquisition', json=data, headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result

    def sample_acquisition_get(self, sample_name):
        """
        returns the acquistion data of this sample

        Args:
             sample_name:

        Returns:
        """
        result = requests.get(f'{self._url}/acquisition/{sample_name}', headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()

    def sample_state(self, sample_name: str, full_response: bool = False):
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
        result = requests.get(f'{self._url}/tracking/{sample_name}', headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")

        if full_response is True:
            return result.json()
        else:
            return result.json()['status']

    def file_handle_by_state(self, sample_name:str, state:str):
        """
        returns the correct file handle for the given sample name in the system
        """

        result = requests.get(f'{self._url}/tracking/{sample_name}', headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")

        states =  result.json()['status']

        for x in states:
            if x['value'] == state and 'fileHandle' in x:
                return x['fileHandle']

        raise Exception("state not found or has no file handle")

    def sample_state_update(self, sample_name: str, state, file_handle: Optional[str] = None):
        """
        updates a sample state in the remote system+

        Args:
            sample_name:
            state:

        Returns:
        """
        data = {
            "sample": sample_name,
            "status": state,
        }

        if file_handle is not None:
            data['fileHandle'] = file_handle

        result = requests.post(f'{self._url}/tracking', json=data, headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result

    def sample_result_as_json(self, sample_name) -> dict:
        result = requests.get(f"{self._url}/result/{sample_name}", headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()

    def get_url(self):
        return self._url

    def get_states(self):
        result = requests.get(f"{self._url}/status", headers=self._header)

        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()

    def load_job(self, job_id):
        """
        loads a job from stasis
        :param job_id:
        :return:
        """
        result = requests.get(f"{self._url}/job/{job_id}", headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()

    def load_job_state(self, job_id):
        """
        loads state details of a job
        :param job_id:
        :return:
        """
        result = requests.get(f"{self._url}/job/status/{job_id}", headers=self._header)
        if result.status_code != 200:
            raise Exception(f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()

    def get_raw_bucket(self):
        """
        :param job_id:
        :return:
        """
        result = requests.get(f"{self._url}/data/raw", headers=self._header)
        if result.status_code != 200:
            raise Exception(f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()['name']

    def get_aggregated_bucket(self):
        """
        :param job_id:
        :return:
        """
        result = requests.get(f"{self._url}/data/zip", headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()['name']

    def get_processed_bucket(self):
        """
        :param job_id:
        :return:
        """
        result = requests.get(f"{self._url}/data/json", headers=self._header)
        if result.status_code != 200:
            raise Exception(f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()['name']

    def download_job_result(self, job: str) -> Optional[str]:
        """
        downloads the result of a job as base64 encoded string
        :return:
        """
        result = requests.get(f"{self._url}/job/result/{job}", headers=self._header)
        if result.status_code == 503:
            return None
        elif result.status_code != 200:
            raise Exception(f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()['content']

    def store_job(self, job: dict):
        """
        stores a job in the system in preparation for scheduling
        :param job:
        :return:
        """
        response = requests.post(f"{self._url}/job/store", json=job, headers=self._header)
        if response.status_code != 200:
            raise Exception(
                f"we observed an error. Status code was {response.status_code} and error was {response.reason}")

    def schedule_job(self, job_id: str):
        """
        scheduels a job for calculation
        :param job_id:
        :return:
        """
        response = requests.put(f"{self._url}/job/schedule/{job_id}", headers=self._header)
        if response.status_code != 200:
            raise Exception(
                f"we observed an error. Status code was {response.status_code} and error was {response.reason}")
        else:
            return json.loads(response.content)
