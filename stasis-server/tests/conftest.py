# Set AWS environment variables if they don't exist before importing moto/boto3
import os

if 'AWS_DEFAULT_REGION' not in os.environ:
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

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

    sqs = moto.mock_sqs()
    sqs.start(
    )

    dynamo = moto.mock_dynamodb2()
    dynamo.start()

    lamb = moto.mock_lambda()
    lamb.start()

    ecs = moto.mock_ecs()
    ecs.start()

    ec2 = moto.mock_ec2()
    ec2.start()

    create_cluster()

    session = boto3.session.Session()
    session.client('sns')
    session.client('s3')

    os.environ["schedule_queue"] = "test_schedule"
    os.environ["topic"] = "UnitTestTopic"
    os.environ["trackingTable"] = "UnitTrackingTable"
    os.environ["acquisitionTable"] = "UnitAcquisitionTable"
    os.environ["resultTable"] = "ResultBucket"
    os.environ["targetTable"] = "UnitTargetTable"
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


def create_cluster():
    from moto.ec2 import utils as ec2_utils
    import simplejson as json

    ec2 = boto3.resource('ec2')
    cluster = boto3.client('ecs')

    cluster.create_cluster(clusterName='carrot')

    cluster.register_task_definition(
        containerDefinitions=[
            {
                'name': 'carrot-runner',
                'command': [
                    'sleep',
                    '360',
                ],
                'cpu': 10,
                'essential': True,
                'image': 'busybox',
                'memory': 10,
            },
        ],
        family='carrot-runner',
        taskRoleArn='',
        volumes=[
        ],
    )

    cluster.register_task_definition(
        containerDefinitions=[
            {
                'name': 'carrot-runner',
                'command': [
                    'sleep',
                    '360',
                ],
                'cpu': 10,
                'essential': True,
                'image': 'busybox',
                'memory': 10,
            },
        ],
        family='secure-carrot-runner',
        taskRoleArn='',
        volumes=[],
    )

    test_instance = ec2.create_instances(
        ImageId="ami-1234abcd",
        MinCount=1,
        MaxCount=1,
    )[0]

    instance_id_document = json.dumps(
        ec2_utils.generate_instance_identity_document(test_instance)
    )

    cluster.register_container_instance(
        cluster="carrot",
        instanceIdentityDocument=instance_id_document
    )

    return cluster
