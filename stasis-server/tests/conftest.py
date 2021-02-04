# Set AWS environment variables if they don't exist before importing moto/boto3
import os

import boto3
import moto
import pytest
import simplejson as json

from stasis.jobs.schedule import store_job, store_sample_for_job
from stasis.schedule.backend import Backend
from stasis.service.Status import REGISTERING, ENTERED
from stasis.tables import get_job_config

os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

from moto.ec2 import utils as ec2_utils


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

    os.environ["runner_env"] = "test"
    os.environ["aggregation_queue"] = "test_aggregation"
    os.environ["schedule_queue"] = "test_schedule"
    os.environ["sample_sync_queue"] = "test_sync_schedule"
    os.environ["topic"] = "UnitTestTopic"
    os.environ["trackingTable"] = "UnitTrackingTable"
    os.environ["acquisitionTable"] = "UnitAcquisitionTable"
    os.environ["resultTable"] = "ResultBucket"
    os.environ["targetTable"] = "CarrotTargetTable"
    os.environ["ecsTable"] = "CarrotECSTable"
    os.environ["dataBucket"] = "data-carrot"
    os.environ["jobTrackingTable"] = "UnitJobTrackingTable"
    os.environ["jobStateTable"] = "UnitJobStateTable"
    os.environ["current_stage"] = "test"
    os.environ["jobQueue"] = "test_job_queue"

    dynamodb = boto3.resource('dynamodb')

    create_cluster()
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
        family="{}-secure-carrot-runner".format(os.getenv("current_stage")),
        taskRoleArn='',
        volumes=[],
    )

    cluster.register_task_definition(
        containerDefinitions=[
            {
                'name': 'carrot-aggregator',
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
        family="{}-secure-carrot-aggregator".format(os.getenv("current_stage")),
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


def pytest_generate_tests(metafunc):
    if "backend" in metafunc.fixturenames:
        metafunc.parametrize("backend", [Backend.FARGATE.value, Backend.LOCAL.value], indirect=True)


@pytest.fixture
def backend(request):
    return Backend(request.param)


@pytest.fixture()
def mocked_10_sample_job_registered_only(backend):
    job = {
        "id": "12345",
        "method": "test",

        "profile": "lcms",
        "state": REGISTERING,
        "resource": backend.value
    }

    result = store_job({'body': json.dumps(job)}, {})

    assert result['statusCode'] == 200

    samples = [
        "abc_0",
        "abc_1",
        "abc_2",
        "abc_3",
        "abc_4",
        "abc_5",
        "abc_6",
        "abc_7",
        "abc_8",
        "abc_9",
    ]

    for sample in samples:
        result = store_sample_for_job({
            'body': json.dumps({
                'job': "12345",
                'sample': sample,
                'meta': {
                    "tracking": [
                        {
                            "state": "entered"
                        },
                        {
                            "state": "acquired",
                            "extension": "d"
                        },
                        {
                            "state": "converted",
                            "extension": "mzml"
                        }
                    ]

                }
            }
            )
        }, {})

        assert result['statusCode'] == 200

    return get_job_config("12345")

@pytest.fixture()
def mocked_10_sample_job(backend):
    job = {
        "id": "12345",
        "method": "test",

        "profile": "lcms",
        "state": REGISTERING,
        "resource": backend.value
    }

    result = store_job({'body': json.dumps(job)}, {})

    assert result['statusCode'] == 200

    samples = [
        "abc_0",
        "abc_1",
        "abc_2",
        "abc_3",
        "abc_4",
        "abc_5",
        "abc_6",
        "abc_7",
        "abc_8",
        "abc_9",
    ]

    for sample in samples:
        result = store_sample_for_job({
            'body': json.dumps({
                'job': "12345",
                'sample': sample,
                'meta': {
                    "tracking": [
                        {
                            "state": "entered"
                        },
                        {
                            "state": "acquired",
                            "extension": "d"
                        },
                        {
                            "state": "converted",
                            "extension": "mzml"
                        }
                    ]

                }
            }
            )
        }, {})

        assert result['statusCode'] == 200
    job = {
        "id": "12345",
        "method": "test",

        "profile": "lcms",
        "state": ENTERED,
        "resource": backend.value
    }

    result = store_job({'body': json.dumps(job)}, {})

    return get_job_config("12345")


@pytest.fixture()
def mocked_10_sample_job_with_classoverride(backend):
    job = {
        "id": "12345",
        "method": "test",

        "profile": "lcms",
        "resource": backend.value
    }

    result = store_job({'body': json.dumps(job)}, {})

    assert result['statusCode'] == 200

    samples = [
        "abc_0",
        "abc_1",
        "abc_2",
        "abc_3",
        "abc_4",
        "abc_5",
        "abc_6",
        "abc_7",
        "abc_8",
        "abc_9",
    ]

    for sample in samples:
        result = store_sample_for_job({
            'body': json.dumps({
                'job': "12345",
                'sample': sample,
                'meta': {
                    "tracking": [
                        {
                            "state": "entered"
                        },
                        {
                            "state": "acquired",
                            "extension": "d"
                        },
                        {
                            "state": "converted",
                            "extension": "mzml"
                        }
                    ],
                    "class": {
                        "name": "test_a",
                        "organ": "test_organ",
                        "species": "test_species"
                    }
                }
            }
            )
        }, {})

        assert result['statusCode'] == 200

    return get_job_config("12345")
