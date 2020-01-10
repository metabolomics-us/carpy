# Set AWS environment variables if they don't exist before importing moto/boto3
import os

import boto3
import moto
import pytest
import simplejson as json
from moto.ec2 import utils as ec2_utils

if 'AWS_DEFAULT_REGION' not in os.environ:
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'


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

    sqs = moto.mock_sqs()
    sqs.start()

    dynamo = moto.mock_dynamodb2()
    dynamo.start()

    lamb = moto.mock_lambda()
    lamb.start()

    ecs = moto.mock_ecs()
    ecs.start()

    ec2 = moto.mock_ec2()
    ec2.start()

    session = boto3.session.Session()
    session.client('sns')
    session.client('s3')

    os.environ["aggregation_queue"] = "test_aggregation"
    os.environ["processing_queue"] = "test_processing"
    os.environ["topic"] = "UnitTestTopic"
    os.environ["trackingTable"] = "UnitTrackingTable"
    os.environ["stasisTrackingTable"] = "UnitStasisTrackingTable"
    os.environ["dataBucket"] = "data-carrot"

    dynamodb = boto3.resource('dynamodb')

    yield
    sqs.stop()
    sns.stop()
    dynamo.stop()
    lamb.stop()
    bucket.stop()
    ecs.stop()
    ec2.stop()

    pass
