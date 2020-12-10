import os

import pytest
from cisclient.client import CISClient
from stasis_client.client import StasisClient

from lcb.node_evaluator import NodeEvaluator


def pytest_generate_tests(metafunc):
    os.environ['CIS_URL'] = 'https://test-api.metabolomics.us/cis'
    os.environ['CIS_API_TOKEN'] = 'rDJfRW6ilG2WooOR72AaE3NqL4m23WvY6ub4FEoS'


@pytest.fixture()
def api_token():
    api_token = os.getenv('CIS_API_TOKEN', '')
    assert api_token is not '', "please ensure you are setting the CIS api token in your env under CIS_API_TOKEN!"

    return {'x-api-key': api_token.strip()}


@pytest.fixture
def cis_cli():
    return CISClient(os.getenv('CIS_URL'), os.getenv('CIS_API_TOKEN'))


@pytest.fixture()
def library_test_name():
    return "soqtof[M-H] | 6530a | c18 | negative"


@pytest.fixture
def stasis_token():
    token = "9MjbJRbAtj8spCJJVTPbP3YWc4wjlW0c7AP47Pmi"
    os.environ['STASIS_TOKEN'] = token
    return token


@pytest.fixture
def stasis_url():
    url =  "https://test-api.metabolomics.us/stasis"
    os.environ['STASIS_URL'] = url
    return url


@pytest.fixture
def stasis_cli(stasis_token, stasis_url):
    return StasisClient(stasis_url, stasis_token)


@pytest.fixture
def node_evaluator(stasis_cli, cis_cli):
    return NodeEvaluator()
