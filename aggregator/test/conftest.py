import json
import os

import pytest
from stasis_client.client import StasisClient


def pytest_generate_tests(metafunc):
    os.environ['STASIS_URL'] = 'https://test-api.metabolomics.us/stasis'
    os.environ['STASIS_API_TOKEN'] = 'lcb-master-293fef66165126eb11f38459da38b291'


@pytest.fixture
def stasis():
    client = StasisClient(os.getenv('STASIS_URL'), os.getenv('STASIS_API_TOKEN'))

    def mock_sample_as_json(sample_name):
        """
        mocking this method out to provide standardized access to the json data
        in a versioned scope
        """
        print("mocking call by loading from file directly: {}".format(sample_name))
        try:
            if 'mzml.json' not in sample_name:
                sample_name = "{}.mzml.json".format(sample_name)
            with open("test/data/{}".format(sample_name), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    client.sample_result_as_json = mock_sample_as_json
    assert "https://test-api.metabolomics.us/stasis" == client.get_url()
    print(f"raw:  {client.get_raw_bucket()}")
    print(f"json: {client.get_processed_bucket()}")
    print(f"zip:  {client.get_aggregated_bucket()}")
    return client


@pytest.fixture()
def api_token():
    api_token = os.getenv('STASIS_API_TOKEN', '')
    assert api_token is not '', "please ensure you are setting the stasis api token in your env under STASIS_API_TOKEN!"
    return {'x-api-key': api_token.strip()}
