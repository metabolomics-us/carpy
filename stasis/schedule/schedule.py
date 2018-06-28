import os
from stasis.schema import __SCHEDULE__
import simplejson as json

from jsonschema import validate

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

    try:
        body = json.loads(event['body'])

        print(body)

        validate(body, __SCHEDULE__)

        import boto3
        overrides = {"containerOverrides": [{
            "name": "carrot-runner",
            "environment": [
                {
                    "name": "SPRING_PROFILES_ACTIVE",
                    "value": "{},{}".format(body['env'], body['mode'])
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

        # fire AWS fargate instance now
        client = boto3.client('ecs')
        response = client.run_task(
            cluster='carrot',  # name of the cluster
            launchType='FARGATE',
            taskDefinition='carrot-runner:1',
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

        # fire status update to track sample is in scheduling
        return response

    except Error:
        return
