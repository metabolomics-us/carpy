# Set AWS environment variables if they don't exist before importing moto/boto3
import json
import os

import moto
import pytest

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
    os.environ["carrot_database"] = "carrot-dev"
    os.environ["carrot_username"] = "postgres"
    os.environ["carrot_password"] = "Fiehnlab2020"
    os.environ["carrot_host"] = "lc-binbase-dev.czbqhgrlaqbf.us-west-2.rds.amazonaws.com"
    os.environ["carrot_port"] = "5432"

    yield
    lamb.stop()

    pass


@pytest.fixture()
def library_test_name() -> str:
    return "soqe[M+H][M+NH4] | QExactive | test | positive"


@pytest.fixture()
def splash_test_name_with_members(library_test_name):
    from cis import compounds
    data = json.loads(compounds.all({'pathParameters': {'library': library_test_name, 'limit': 100000}}, {})['body'])

    for num, splash in enumerate(data):
        response = compounds.get_members({'pathParameters': {'library': library_test_name, 'splash': splash}}, {})
        if response['statusCode'] == 200:
            result = (data[num], library_test_name)
            return result

    raise Exception(f"did not find a standard with members in {library_test_name}")
