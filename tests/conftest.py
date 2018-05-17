import pytest
import moto
import boto3
import os


@pytest.fixture
def requireMocking():
    """
        method which should be called before all other methods in tests. It basically configures our
        mocking context for stasis
        """

    sns = moto.mock_sns()
    sns.start()

    dynamo = moto.mock_dynamodb2()
    dynamo.start()

    lamb = moto.mock_lambda()
    lamb.start()

    bucket = moto.mock_s3()
    bucket.start()

    session = boto3.session.Session()
    session.client('sns')

    os.environ["topic"] = "UnitTestTopic"
    os.environ["trackingTable"] = "UnitTrackingTable"
    os.environ["acquisitionTable"] = "UnitAcquisitionTable"
    os.environ["resultTable"] = "ResultBucket"

    dynamodb = boto3.resource('dynamodb')
    dynamodb.create_table(
        TableName=os.environ["trackingTable"],
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    dynamodb.create_table(
        TableName=os.environ["acquisitionTable"],
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    dynamodb.create_table(
        TableName=os.environ["resultTable"],
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }

    )

    print("creating test bucket")

    try:
        boto3.client('s3').create_bucket(Bucket=os.environ["resultTable"])
    except botocore.errorfactory.BucketAlreadyExists:
        print("sorry this bucket BucketAlreadyExists")


    yield
    sns.stop()
    dynamo.stop()
    lamb.stop()
    bucket.stop()

    pass
