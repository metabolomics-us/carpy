# Set AWS environment variables if they don't exist before importing moto/boto3
import os
import sys
import urllib.parse

import moto
import pytest
import simplejson as json
from loguru import logger

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="conftest", level="INFO", backtrace=True,
           diagnose=True)

os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'


@pytest.fixture
def requireMocking():
    """
    method which should be called before all other methods in tests. It basically configures our
    mocking context for stasis
    """

    lamb = moto.mock_lambda()
    lamb.start()

    os.environ["current_stage"] = "test"
    os.environ["carrot_database"] = "cis-test"
    os.environ["carrot_username"] = "postgres"
    os.environ["carrot_password"] = "Fiehnlab2020"
    os.environ["carrot_host"] = "lc-binbase-dev.czbqhgrlaqbf.us-west-2.rds.amazonaws.com"
    os.environ["carrot_port"] = "5432"

    yield
    lamb.stop()

    pass


@pytest.fixture()
def library_test_name() -> str:
    return "soqtof[M-H] | 6530a | c18 | negative"


@pytest.fixture()
def pos_library_test_name() -> str:
    return "soqe[M+H][M+NH4] | QExactive | test | positive"


@pytest.fixture()
def splash_test_name_with_members(pos_library_test_name, request):
    from cis import compounds
    result = request.config.cache.get("cis/members", None)

    if result is not None:
        print(f"using cached object: {result}")
        return result
    else:
        print("loading all, takes forever and should be cached instead...")
        data = json.loads(
            compounds.get_sorted({'pathParameters': {'library': urllib.parse.quote(pos_library_test_name)},
                                  'queryStringParameters': {'limit': 100000}}, {})['body'])

    for num, splash in enumerate(data):
        response = compounds.get_members({'pathParameters': {'library': urllib.parse.quote(pos_library_test_name),
                                                             'splash': splash}}, {})
        if response['statusCode'] == 200:
            result = (data[num], pos_library_test_name)

            request.config.cache.set("cis/members", result)
            return result

    raise Exception(f"did not find a standard with members in {pos_library_test_name}")


@pytest.fixture()
def splash_test_name_with_no_members(pos_library_test_name, request):
    from cis import compounds
    result = request.config.cache.get("cis/no_members", None)

    if result is not None:
        print(f"using cached object: {result}")
        return result
    else:
        print("loading all, takes forever and should be cached instead...")
        data = json.loads(
            compounds.get_sorted({'pathParameters': {'library': urllib.parse.quote(pos_library_test_name)},
                                  'queryStringParameters': {'limit': 100000}}, {})['body'])

    for num, splash in enumerate(data):
        response = compounds.get_members({'pathParameters': {'library': urllib.parse.quote(pos_library_test_name),
                                                             'splash': splash}}, {})
        if response['statusCode'] == 404:
            result = (data[num], pos_library_test_name)

            request.config.cache.set("cis/no_members", result)
            return result

    raise Exception(f"did not find a standard with no_members in {pos_library_test_name}")


@pytest.fixture()
def target_id():
    return '199'


@pytest.fixture()
def user_id():
    return 'test_user'


@pytest.fixture()
def sample_name():
    return 'NIH_Lip_Std_CSH_POS_Brain_01'


@pytest.fixture()
def range_search():
    return {'pmzval': 279.1598, 'pmzacc': 0.01, 'rival': 219, 'riacc': 10}


@pytest.fixture()
def annotated_target():
    return {"id": 40285, "splash": "splash10-0002-5410090000-af60d3205786a584beac", "count": 3}
