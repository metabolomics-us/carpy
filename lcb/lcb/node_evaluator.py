import json
import os
from lcb.evaluator import Evaluator

import boto3
import docker
from boto3 import Session


class NodeEvaluator(Evaluator):
    """
    provides a simple node for running calculation tasks for us
    """

    def evaluate(self, args: dict):
        mapping = {
            'single': self.local
        }

        results = {}

        for x in args.keys():
            if x in mapping:
                if args[x] is not False or str(args[x]) != 'False':
                    results[x] = mapping[x](args)
        return results

    def local(self, args):
        # connect to queue

        # Create SQS client
        sqs = boto3.client('sqs')

        # todo get correct queue name from stasis
        queue_url = "https://sqs.us-west-2.amazonaws.com/702514165722/StasisScheduleQueue-dev_FARGATE"
        # start docker
        client = docker.from_env()

        while True:
            # Receive message from SQS queue
            response = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=[
                    'SentTimestamp'
                ],
                MaxNumberOfMessages=1,
                MessageAttributeNames=[
                    'All'
                ],
                VisibilityTimeout=0,
                WaitTimeSeconds=0
            )

            message = response['Messages'][0]
            body = message['Body']

            config = json.loads(json.loads(body)['default'])

            session = Session()
            credentials = session.get_credentials()
            current_credentials = credentials.get_frozen_credentials()
            environment = {
                'AWS_ACCESS_KEY_ID': current_credentials.access_key,
                'AWS_DEFAULT_REGION': 'us-west-2',
                'AWS_SECRET_ACCESS_KEY': current_credentials.secret_key,
                'STASIS_KEY': os.getenv('STASIS_API_TOKEN'),
                'STASIS_URL': os.getenv('STASIS_API_URL'),
            }

            if config['stasis-service'] == 'secure-carrot-runner':
                environment['SPRING_PROFILES_ACTIVE'] = "{}{},{}".format('aws', 'dev', config['profile'])
                environment['CARROT_SAMPLE'] = config['sample']
                environment['CARROT_METHOD'] = config['method']
                environment['CARROT_MODE'] = config['profile']
                print("start SAMPLE process environment")
                container = client.containers.run("702514165722.dkr.ecr.us-west-2.amazonaws.com/carrot:latest",
                                                  environment=environment, detach=True, auto_remove=True)
                # run image
                for line in container.logs(stream=True):
                    print(str(line.strip()))
                pass

                receipt_handle = message['ReceiptHandle']

                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle
                )

            elif config['stasis-service'] == 'secure-carrot-aggregator':
                environment['CARROT_JOB'] = config['job']
                print("start JOB process environment")
                container = client.containers.run("702514165722.dkr.ecr.us-west-2.amazonaws.com/carrot:agg-latest",
                                                  environment=environment, detach=True, auto_remove=True)
                # run image
                for line in container.logs(stream=True):
                    print(str(line.strip()))
                pass

                receipt_handle = message['ReceiptHandle']

                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle
                )

            else:
                print("not yet supported!!!")
                print(json.dump(body, indent=4))