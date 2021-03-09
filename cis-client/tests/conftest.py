import os

import pytest

from cisclient.client import CISClient


def pytest_generate_tests(metafunc):
    os.environ['CIS_URL'] = 'https://test-api.metabolomics.us/cis'
    os.environ['CIS_API_TOKEN'] = 'aidfca01Xe9sBdS8LnVv9NPJQA1WVZU58gD8Dmm2'


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


@pytest.fixture()
def splash_test_name(cis_cli, library_test_name):
    result = cis_cli.get_compounds(library=library_test_name, autopage=False)

    return (result[0], library_test_name)


@pytest.fixture()
def target_id():
    return '361'


@pytest.fixture()
def sample_id():
    return 'PlasmaBiorec002_MX524916_negCSH_postSOP010'
