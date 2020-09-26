import json
import os
import traceback
from time import time, sleep

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
        """
        connects to the queue and processes received messages one at a time
        """
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

            if 'Messages' in response and len(response['Messages']) > 0:

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

                try:
                    if config['stasis-service'] == 'secure-carrot-runner':
                        self.process_single_sample(client, config, environment, message, queue_url, sqs, args)

                    elif config['stasis-service'] == 'secure-carrot-aggregator':
                        self.process_aggregation(client, config, environment, message, queue_url, sqs, args)
                    else:
                        print("not yet supported!!!")
                        print(json.dumps(body, indent=4))
                except Exception as e:
                    traceback.print_exc()
                    print("major error observed which breaks!")
            else:
                print("sleeping for 5 seconds since queue is empty")
                sleep(5)

    def process_aggregation(self, client, config, environment, message, queue_url, sqs, args):
        """
        processes a local aggregation in this node
        """
        environment['CARROT_JOB'] = config['job']
        environment['STASIS_KEY'] = os.getenv('STASIS_API_TOKEN')
        environment['STASIS_URL'] = os.getenv('STASIS_API_URL')

        print("start JOB process environment")
        container = client.containers.run("702514165722.dkr.ecr.us-west-2.amazonaws.com/carrot:agg-latest",
                                          environment=environment, detach=True, auto_remove=False)
        # run image
        for line in container.logs(stream=True):
            print(str(line.strip()))
        pass
        receipt_handle = message['ReceiptHandle']
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

    def process_single_sample(self, client, config, environment, message, queue_url, sqs, args):
        """
        procees a single sample
        """

        springProfiles = self.optimize_profiles(args, config)

        print(f"generated spring profiles to activate: {springProfiles}")
        environment['SPRING_PROFILES_ACTIVE'] = springProfiles
        environment['CARROT_SAMPLE'] = config['sample']
        environment['CARROT_METHOD'] = config['method']
        environment['CARROT_MODE'] = config['profile']

        for env in args['env']:
            environment[env] = os.getenv(env)

        print("start SAMPLE process environment")

        docker_args = {
            'image': "702514165722.dkr.ecr.us-west-2.amazonaws.com/carrot:latest",
            'environment': environment, 'detach': True,
            'auto_remove': args['keep'] is False
        }

        for docker in args['docker']:
            key, value = docker.split("=")
            docker_args[key] = value

        print(f"utilizing docker configuration:\n {json.dumps(docker_args, indent=4)}")
        container = client.containers.run(**docker_args)

        # run image
        for line in container.logs(stream=True):
            print(str(line.strip()))
        pass
        receipt_handle = message['ReceiptHandle']
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

    @staticmethod
    def optimize_profiles(args, config):
        """
        optimizes the profiles to be activate or deactivated in the processor
        """
        springProfiles = config['profile'].split(",")
        for add in args['add']:
            springProfiles.append(add)
        for remove in args['remove']:
            if remove in springProfiles:
                springProfiles.remove(remove)
        return ",".join(springProfiles).strip()
