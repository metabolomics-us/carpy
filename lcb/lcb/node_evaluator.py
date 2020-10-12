import json
import os
import traceback
from time import sleep
from typing import Optional

import boto3
import docker

from lcb.evaluator import Evaluator


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
        client = self.buildClient()

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

                environment = self.get_aws_env()

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

    def get_aws_env(self):
        return self._secret_config

    def buildClient(self):
        client = docker.from_env()
        return client

    def process_aggregation(self, client, config, environment, message, queue_url, sqs, args):
        """
        processes a local aggregation in this node
        """
        environment['CARROT_JOB'] = config['job']

        print("start JOB process environment")
        container = client.containers.run("702514165722.dkr.ecr.us-west-2.amazonaws.com/carrot:agg-latest",
                                          environment=environment, detach=True, auto_remove=False)
        self.execute_container(container, message, queue_url, sqs)

    def process_steac(self, client, config, environment, message: Optional, queue_url: Optional, sqs: Optional, args):
        """
        processes a local aggregation in this node
        """
        environment['CARROT_METHOD'] = config['method']
        print("start JOB process environment")
        container = client.containers.run("702514165722.dkr.ecr.us-west-2.amazonaws.com/steac:latest",
                                          environment=environment, detach=True, auto_remove=False)
        self.execute_container(container, message, queue_url, sqs)

    def execute_container(self, container, message, queue_url, sqs):
        """
        executes the specied container and logs out the content
        """
        # run image
        for line in container.logs(stream=True):
            print(str(line.strip()))

        if message is not None:
            receipt_handle = message['ReceiptHandle']
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )

    def process_single_sample(self, client, config, environment, message, queue_url, sqs, args):
        """
        procees a single sample
        """

        spring_profiles = self.optimize_profiles(args, config)

        print(f"generated spring profiles to activate: {spring_profiles}")
        environment['SPRING_PROFILES_ACTIVE'] = spring_profiles
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
        self.execute_container(container, message, queue_url, sqs)

    @staticmethod
    def optimize_profiles(args, config: Optional[dict] = {}):
        """
        optimizes the profiles to be activate or deactivated in the processor
        """
        springProfiles = config['profile'].split(",") if "profile" in config else []
        for add in args['add']:
            springProfiles.append(add)
        for remove in args.get('remove'):
            if remove in springProfiles:
                springProfiles.remove(remove)
        return ",".join(springProfiles).strip()

    @staticmethod
    def configure_node(main_parser, sub_parser):

        parser = sub_parser.add_parser(name="node", help="starts a node for computations")

        parser.add_argument("-s", "--single", help="runs a single node", action="store_true",
                            required=True)
        parser.add_argument("-r", "--remove",
                            help="remove a profile from instructions. In case we don't want to use it right now",
                            action="append",
                            required=False, default=[])
        parser.add_argument("-a", "--add", help="add a profile to the calculation instructions", action="append",
                            required=False, default=['awsdev'])

        parser.add_argument("-k", "--keep", help="keep the executed docker container and logs for diagnostics",
                            action="store_true",
                            required=False, default=False)
        parser.add_argument("-d", "--docker", help="additional arguments for the docker container to be run",
                            action="append",
                            required=False, default=[])
        parser.add_argument("-e", "--env",
                            help="forward the specified env variable from the host to the docker container",
                            action="append", required=False, default=[])
        return parser
