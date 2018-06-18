
# Set AWS environment variables if they don't exist before importing moto/boto3
import os

if 'AWS_DEFAULT_REGION' not in os.environ:
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-2'

import pytest
import moto
import boto3


@pytest.fixture
def requireMocking():
    """
    method which should be called before all other methods in tests. It basically configures our
    mocking context for stasis
    """

    bucket = moto.mock_s3()
    bucket.start()

    sns = moto.mock_sns()
    sns.start()

    dynamo = moto.mock_dynamodb2()
    dynamo.start()

    lamb = moto.mock_lambda()
    lamb.start()

    session = boto3.session.Session()
    session.client('sns')
    session.client('s3')

    os.environ["topic"] = "UnitTestTopic"
    os.environ["trackingTable"] = "UnitTrackingTable"
    os.environ["acquisitionTable"] = "UnitAcquisitionTable"
    os.environ["resultTable"] = "ResultBucket"

    dynamodb = boto3.resource('dynamodb')

    yield
    sns.stop()
    dynamo.stop()
    lamb.stop()
    bucket.stop()

    pass
