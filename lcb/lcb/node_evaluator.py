import base64
import json
import os
import traceback
from time import sleep
from typing import Optional

import boto3
import docker

from lcb.evaluator import Evaluator
from lcb.load_secrets import Secrets


class NodeEvaluator(Evaluator):
    """
    provides a simple node for running calculation tasks for us
    """

    def __init__(self, secret: Optional[Secrets] = None):
        super().__init__(secret)

        self.registry = "702514165722.dkr.ecr.us-west-2.amazonaws.com"

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
        environment = self.get_aws_env()
        # Create SQS client
        sqs = boto3.client('sqs')

        # todo get correct queue name from stasis
        queue_url = "https://sqs.us-west-2.amazonaws.com/702514165722/StasisScheduleQueue-dev_FARGATE"
        # start docker

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

                client = self.buildClient()
                message = response['Messages'][0]
                body = message['Body']

                config = json.loads(json.loads(body)['default'])

                print("received new message to process...")
                try:
                    if config['stasis-service'] == 'secure-carrot-runner':
                        print("it's a sample we need to process")
                        self.process_single_sample(client, config, environment, message, queue_url, sqs, args)
                    elif config['stasis-service'] == 'secure-carrot-aggregator':
                        print("it's an aggregation to run")
                        self.process_aggregation(client, config, environment, message, queue_url, sqs, args)
                    elif config['stasis-service'] == 'secure-carrot-steac':
                        print("it's a steac process")
                        self.process_steac(client, config, environment, message, queue_url, sqs, args)
                    else:
                        print("not yet supported!!!")
                        print(json.dumps(body, indent=4))

                    print()
                except Exception as e:
                    traceback.print_exc()
                    print("major error observed which breaks!")
            else:
                #                print("sleeping for 5 seconds since queue is empty")
                print(f"queue is empty, nothing todo: ${queue_url}")
                sleep(5)
            if args['once'] is True:
                print("shutting down node, only was supposed to process 1 message!")
                return

    def get_aws_env(self):
        return self._secret_config.copy()

    def buildClient(self):

        print("building client for ecr")
        ecr = boto3.client('ecr')

        token = ecr.get_authorization_token()
        username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
        registry = token['authorizationData'][0]['proxyEndpoint'].replace("https://", "")

        client = docker.from_env()

        client.login(
            username=username,
            password=password,
            registry=registry,
            reauth=True
        )

        print("success")
        return client

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

        # this overrides variables in lc binbase, required to connect to certain services

        environment['STASIS_BASEURL'] = environment['STASIS_URL']
        environment['STASIS_KEY'] = environment['STASIS_TOKEN']

        for env in args['env']:
            environment[env] = os.getenv(env)

        print("start SAMPLE process environment")

        client.api.pull(f"{self.registry}/carrot:latest")

        docker_args = {
            'image': f"{self.registry}/carrot:latest",
            'environment': environment, 'detach': True,
            'auto_remove': False
        }

        for d in args['docker']:
            key, value = d.split("=")
            docker_args[key] = value

        self._printenv(docker_args)
        container = client.containers.run(**docker_args)
        self.execute_container(container, message, queue_url, sqs, args, environment)

    def process_aggregation(self, client, config, environment, message, queue_url, sqs, args):
        """
        processes a local aggregation in this node
        """
        environment['CARROT_JOB'] = config['job']

        client.api.pull(f"{self.registry}/agg:latest")
        print(f"start aggregation process environment")

        docker_args = {
            'image': f"{self.registry}/agg:latest",
            'environment': environment, 'detach': True,
            'auto_remove': True
        }

        self._printenv(docker_args)
        container = client.containers.run(**docker_args)
        self.execute_container(container, message, queue_url, sqs, args, environment)

    def _printenv(self, docker_args, indent=""):
        """
        prints out the given args in an orderly fashin
        """
        for e in docker_args:

            if isinstance(docker_args[e], dict):
                print(f"{indent}{e} =>")
                self._printenv(docker_args[e], indent + "\t")
            else:
                print(f"{indent}{e} = {docker_args[e]}")

    def process_steac(self, client, config, environment, message: Optional, queue_url: Optional, sqs: Optional, args):
        """
        processes a local aggregation in this node
        """
        environment['CARROT_METHOD'] = config['method']
        print("start STEAC process environment")
        client.api.pull(f"{self.registry}/steac:latest")
        container = client.containers.run(f"{self.registry}/steac:latest",
                                          environment=environment, detach=True, auto_remove=False)
        self.execute_container(container, message, queue_url, sqs, args, environment)

    def execute_container(self, container, message, queue_url, sqs, args, environment):
        """
        executes the specied container and logs out the content
        """

        if args['log'] is True:
            # run image
            for line in container.logs(stream=True):
                print(str(line.strip()))

        print(f"waiting for shutdown of container now: {container}")
        result = container.wait()

        statusCode = result['StatusCode']

        if message is not None and statusCode == 0:
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
        elif message is not None:
            print(
                f"returning message due to an invalid status code: {statusCode} and executed container was: {container}")
            self._printenv(environment, indent="\t\t => \t")
            print("associated container log file:")
            for line in container.logs(stream=True):
                print(f"\t\t{str(line.strip())}")
            print()
            try:
                sqs.change_message_visibility(
                    VisibilityTimeout=0,
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                if args['log']:
                    print(f"warning, we observed an error while sending back the message {message}, error was {e}")
                    traceback.print_exc()

        if args['keep'] is False:
            print(f"cleaning up container with id {container.id}")
            container.remove()

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

        parser.add_argument("-o", "--once", help="processes one message and shutdown", action="store_true",
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

        parser.add_argument("-l", "--log", help="do you want to log the spawned docker container to stdout?",
                            action="store_true",
                            required=False, default=False)

        parser.add_argument("-d", "--docker", help="additional arguments for the docker container to be run",
                            action="append",
                            required=False, default=[])
        parser.add_argument("-e", "--env",
                            help="forward the specified env variable from the host to the docker container",
                            action="append", required=False, default=[])

        return parser
