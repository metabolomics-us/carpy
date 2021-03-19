import os
import sys

import pytest
from loguru import logger

from cisclient.client import CISClient

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="conftest", level="INFO", backtrace=True,
           diagnose=True)


def pytest_generate_tests(metafunc):
    os.environ['CIS_URL'] = 'https://test-api.metabolomics.us/cis'
    os.environ['CIS_API_TOKEN'] = 'aidfca01Xe9sBdS8LnVv9NPJQA1WVZU58gD8Dmm2'


@logger.catch
@pytest.fixture()
def api_token():
    api_token = os.getenv('CIS_API_TOKEN', '')
    assert api_token is not '', "please ensure you are setting the CIS api token in your env under CIS_API_TOKEN!"

    return {'x-api-key': api_token.strip()}


@logger.catch
@pytest.fixture
def cis_cli():
    return CISClient(os.getenv('CIS_URL'), os.getenv('CIS_API_TOKEN'))


@logger.catch
@pytest.fixture()
def library_test_name():
    return "soqe[M+H][M+NH4] | QExactive | test | positive"


@logger.catch
@pytest.fixture()
def splash_test_name(cis_cli, library_test_name):
    result = cis_cli.get_compounds(library=library_test_name, autopage=False)

    return (result[0], library_test_name)


@logger.catch
@pytest.fixture()
def splash_test_name_with_members(cis_cli, library_test_name):
    return ("splash10-001i-1900000000-3b9584bc9a188a381979", library_test_name)


@logger.catch
@pytest.fixture()
def target_id():
    return '199'


@logger.catch
@pytest.fixture()
def sample_id():
    return 'NIH_Lip_Std_CSH_POS_Brain_01'
