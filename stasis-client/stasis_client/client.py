import os
import shutil
from time import sleep
from typing import Optional, List

import boto3
import boto3.s3
import requests
import simplejson as json
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as CE
from urllib3 import Retry


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

        retry_strategy = Retry(
            total=500,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http = requests.Session()

    def schedule_sample_for_computation(self, sample_name: str, method: str, profile: str,
                                        resource: str = "FARGATE") -> dict:
        """
        schedules a sample for dataprocessing
        """
        result = self.http.post(f"{self._url}/schedule",
                                json={'sample': sample_name, 'method': method, 'profile': profile,
                                      'resource': resource, 'secured': True}, headers=self._header)

        if result.status_code != 200:
            raise Exception(
                f"scheduling failed for {sample_name} , profile {profile}, resource {resource} and method {method}")
        else:
            return result.json()

    def sample_raw_data_exists(self, sample_name) -> bool:
        """
        checks if the raw data exist
        """
        result = self.http.head(f"{self._url}/sample/{sample_name}")

        if result.status_code == 200:
            return True
        elif result.status_code == 404:
            return False
        else:
            raise Exception(
                "error checkign state, status code was {} for sample {}".format(result.status_code, sample_name))

    def sample_acquisition_create(self, data: dict):
        """
        adds sample metadata info to stasis
        Args:
             data: the data object containing the aquisiton description
        Returns:
        """
        result = self.http.post(f'{self._url}/acquisition', json=data, headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason} for data {data}")
        return result

    def sample_acquisition_get(self, sample_name) -> dict:
        """
        returns the acquistion data of this sample

        Args:
             sample_name:

        Returns:
        """
        result = self.http.get(f'{self._url}/acquisition/{sample_name}', headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason} for sample {sample_name}")
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
        result = self.http.get(f'{self._url}/tracking/{sample_name}', headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason} for {sample_name}")

        if full_response is True:
            return result.json()
        else:
            return result.json()['status']

    def file_handle_by_state(self, sample_name: str, state: str) -> str:
        """
        returns the correct file handle for the given sample name in the system
        """

        result = self.http.get(f'{self._url}/tracking/{sample_name}', headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason} for {sample_name} and {state}")

        states = result.json()['status']

        for x in states:
            if x['value'] == state and 'fileHandle' in x:
                return x['fileHandle']

        raise Exception("state not found or has no file handle for {} and state".format(sample_name, state))

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

        result = self.http.post(f'{self._url}/tracking', json=data, headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason} and {sample_name} in {state} with {file_handle}")
        return result

    def sample_result_as_json(self, sample_name) -> dict:
        """
        download a sample result as json from the result bucket we are using

        :param sample_name:
        :return:
        """

        bucket_name = self.get_processed_bucket()
        try:
            boto3.client('s3').create_bucket(Bucket=bucket_name,
                                             CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
        except Exception as e:
            pass

        file = self.file_handle_by_state(sample_name, "exported")

        content = boto3.client('s3').get_object(Bucket=bucket_name, Key="{}".format(file))['Body'].read().decode('utf-8')
        return json.loads(content)

    def get_url(self):
        return self._url

    def get_states(self):
        result = self.http.get(f"{self._url}/status", headers=self._header)

        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()

    def load_job(self, job_id) -> List[dict]:
        """
        loads a job from stasis
        :param job_id:
        :return:
        """

        data = []

        def fetch(job, last=None):
            if last is None:
                result = self.http.get(f"{self._url}/job/{job}", headers=self._header)
            else:
                result = self.http.get(f"{self._url}/job/{job}/{last}", headers=self._header)
            if result.status_code != 200 and last is None:
                raise Exception(
                    f"we observed an error. Status code was {result.status_code} and error was {result.reason} for job {job_id}")
            elif result.status_code == 200:
                result = json.loads(result.content)
                for x in result:
                    data.append(x)

                return result
            else:
                return []

        result = fetch(job_id)

        while len(result) == 10:
            result = fetch(job=job_id, last=data[-1]['id'])

        return data

    def load_job_state(self, job_id) -> dict:
        """
        loads state details of a job
        :param job_id:
        :return:
        """
        result = self.http.get(f"{self._url}/job/status/{job_id}", headers=self._header)
        if result.status_code != 200:
            raise Exception(
                f"we observed an error. Status code was {result.status_code} and error was {result.reason} for job {job_id}")
        return result.json()

    def get_raw_bucket(self) -> str:
        """
        :param job_id:
        :return:
        """
        result = self.http.get(f"{self._url}/data/raw", headers=self._header)
        if result.status_code != 200:
            raise Exception(f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()['name']

    def get_aggregated_bucket(self) -> str:
        """
        :param job_id:
        :return:
        """
        result = self.http.get(f"{self._url}/data/zip", headers=self._header)
        if result.status_code != 200: raise Exception(
            f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()['name']

    def get_processed_bucket(self) -> str:
        """
        :param job_id:
        :return:
        """
        result = self.http.get(f"{self._url}/data/json", headers=self._header)
        if result.status_code != 200:
            raise Exception(f"we observed an error. Status code was {result.status_code} and error was {result.reason}")
        return result.json()['name']

    def upload_job_result(self, job: str, directory: str):
        """
        uploads the content of the given directory to the remote storage facility.
        """

        bucket_name = self.get_aggregated_bucket()
        print("zipping data and uploading it to the result bucket: {}. File name will be {}.{}".format(
            bucket_name, job, "zip"))
        shutil.make_archive(f"result/{job}", 'zip', directory)

        try:
            boto3.client('s3').create_bucket(Bucket=bucket_name,
                                             CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
        except Exception as e:
            pass

        # upload new file
        return boto3.client('s3').upload_file(Filename=f"result/{job}.zip", Bucket=bucket_name, Key=f"{job}.zip")

    def download_job_result(self, job: str) -> Optional[str]:
        """
        downloads the result of a job as base64 encoded string

        #TODO refactor to use buckets instead, due to very large file sizes
        :return:
        """
        result = self.http.get(f"{self._url}/job/result/{job}", headers=self._header)
        if result.status_code == 503:
            return None
        elif result.status_code != 200:
            raise Exception(
                f"we observed an error. Status code was {result.status_code} and error was {result.reason} for job {job}")
        return result.json()['content']

    def store_job(self, job: dict, enable_progress_bar: bool = False):
        """
        stores a job in the system in preparation for scheduling
        :param job:
        :return:
        """
        meta = job.pop('meta', {})
        samples = job.pop('samples')

        response = self.http.post(f"{self._url}/job/store", json=job, headers=self._header)

        if response.status_code != 200:
            raise Exception(
                f"we observed an error. Status code was {response.status_code} and error was {response.reason} for {job}")

        from tqdm import tqdm

        for sample in tqdm(samples, desc="storing sample definitions", disable=enable_progress_bar is False):
            finished = 0

            while finished < 100:
                try:
                    res = requests.post(f"{self._url}/job/sample/store", json={
                        "sample": sample,
                        "job": job['id'],
                        "meta": meta
                    }, headers=self._header)

                    finished = 100
                    if res.status_code != 200:
                        raise Exception(
                            f"we observed an error. Status code was {response.status_code} and error was {response.reason} for {job}")
                except CE as e:
                    finished = finished + 1
                    sleep(1000)

    def schedule_job(self, job_id: str) -> dict:
        """
        scheduels a job for calculation
        :param job_id:
        :return:
        """
        response = self.http.put(f"{self._url}/job/schedule/{job_id}", headers=self._header)
        if response.status_code != 200:
            raise Exception(
                f"we observed an error. Status code was {response.status_code} and error was {response.reason} for {job_id}")
        else:
            return json.loads(response.content)

    def force_sync(self, job_id) -> dict:
        response = self.http.put(f"{self._url}/job/sync/{job_id}", headers=self._header)
        if response.status_code != 200:
            raise Exception(
                f"we observed an error. Status code was {response.status_code} and error was {response.reason} for {job_id}")
        else:
            return json.loads(response.content)


