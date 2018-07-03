import os

import simplejson as json
from jsonschema import validate

from stasis.headers import __HTTP_HEADERS__
from stasis.schema import __SCHEDULE__
from stasis.tracking.create import create


def schedule(event, context):
    """
    triggers a new calculation task on the fargate server
    :param event:
    :param context:
    :return:
    """
    """
        submits a new task to the cluster - a fargate task will run it

    :param configuration:
    :param user:
    :return:
    """
    body = json.loads(event['body'])

    print(body)
    try:

        validate(body, __SCHEDULE__)

        import boto3
        overrides = {"containerOverrides": [{
            "name": "carrot-runner",
            "environment": [
                {
                    "name": "SPRING_PROFILES_ACTIVE",
                    "value": "{},{}".format(body['env'], body['profile'])
                },
                {
                    "name": "CARROT_SAMPLE",
                    "value": "{}".format(body['sample'])
                },
                {
                    "name": "CARROT_METHOD",
                    "value": "{}".format(body['method'])
                }
            ]
        }]}

        version = "1"

        if "task_version" in body:
            version = body["task_version"]

        print("utilizing version: {}".format(version))

        # fire AWS fargate instance now
        client = boto3.client('ecs')
        response = client.run_task(
            cluster='carrot',  # name of the cluster
            launchType='FARGATE',
            taskDefinition='carrot-runner:{}'.format(version),
            count=1,
            platformVersion='LATEST',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        # we need at least 2, to insure network stability
                        os.environ.get('SUBNET', 'subnet-064fbf05a666c6557')],
                    'assignPublicIp': 'ENABLED'
                }
            },
            overrides=overrides,
        )

        create({"body": json.dumps({'sample': body['sample'], 'status': 'scheduled'})}, {})

        # fire status update to track sample is in scheduling

        return {
            'body': json.dumps(response),
            'statusCode': 200,
            'headers': __HTTP_HEADERS__
        }

    except Exception as e:

        print(e)
        create({"body": json.dumps({'sample': body['sample'], 'status': 'failed'})}, {})

        return {
            'body': json.dumps(str(e)),
            'statusCode': 503,
            'headers': __HTTP_HEADERS__
        }
