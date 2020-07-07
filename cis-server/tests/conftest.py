# Set AWS environment variables if they don't exist before importing moto/boto3
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
def library_test_name():
    return "soqtof[M-H] | 6530a | c18 | negative"


@pytest.fixture()
def splash_test_name():
    return ("splash10-001i-0090000200-bccd4f06d0b5c3e48c6a", "soqe[M-H] | QExactive | test | negative")
