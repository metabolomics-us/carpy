import json
import os
import requests
import time

from pathlib import Path
from typing import List


stasis_url = "https://api.metabolomics.us/stasis"
test_url = "https://test-api.metabolomics.us/stasis"


def _api_token():
    api_token = os.getenv('PROD_STASIS_API_TOKEN', '').strip()
    if api_token is '':
        raise requests.RequestException("Missing authorization token")

    return {'x-api-key': api_token}


def print_response(response):
    print(f'{response.status_code} -- {response.reason}')
    print(json.dumps(response.json(), indent=2))


def get_experiment_files(experiment) -> List[str]:
    """
    NOT USED ATM
    Calls the stasis api to get a list files for an experiment
    :param experiment: name of experiment for which to get the list of files
    :return: dictionary with results or {error: msg}
    """
    print(f'{time.strftime("%H:%M:%S")} - Getting experiment files')
    response = requests.get(stasis_url + '/experiment/' + experiment, headers=_api_token())

    files = []
    if response.status_code == 200:
        files = [item['sample'] for item in response.json()]

    return files


def get_sample_tracking(filename):
    """
    NOT USED ATM
    Calls the stasis api to get the tracking status for a single file
    :param filename: name of file to get tracking info from
    :return: dictionary with tracking or {error: msg}
    """
    print(f'{time.strftime("%H:%M:%S")} - Getting filename status')
    response = requests.get(stasis_url + '/tracking/' + filename, headers=_api_token())

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "no tracking info"}


def get_sample_metadata(filename, log):
    """
    Calls the stasis api to get the metadata for a single file
    :param filename: name of file to get metadata from
    :param log:
    :return: dictionary with metadata or {error: msg}
    """
    response = requests.get(stasis_url + '/acquisition/' + filename, headers=_api_token())

    if log:
        print_response(response)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "no metadata info"}


def get_file_results(filename, log, count, local_dir=None, save=False):
    """
    Calls the stasis api to get the results for a single file
    :param filename: name of file to get results from
    :param log:
    :param count:
    :return: dictionary with results or {error: msg}
    """

    if filename[-5:] == '.mzml':
        filename = filename[:-5]

    if local_dir and Path(local_dir).is_dir() and (Path(local_dir) / filename).exists():
        return json.load((Path(local_dir) / filename).open())
    else:
        print(f'{time.strftime("%H:%M:%S")} - [{count}] Getting results for file \'{filename}\'')
        response = requests.get(stasis_url + "/result/" + filename, headers=_api_token())

        if response.status_code == 200:
            data = response.json()
            data['metadata'] = get_sample_metadata(filename, log)

            # Save data locally if requested
            if save and local_dir:
                with (Path(local_dir) / filename).open('w') as fout:
                    print(json.dumps(data, indent=2), file=fout)
        else:
            data = {'error': f'no results. {response.reason}'}

        if log:
            print_response(response)

        return data
