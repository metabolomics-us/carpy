import os
from time import sleep

from cisclient.client import CISClient
from stasis_client.client import StasisClient

from lcb.evaluator import Evaluator
from lcb.node_evaluator import NodeEvaluator


class SteacEvaluator(Evaluator):
    """
    executes aggregations locally
    """

    def evaluate(self, args: dict):
        mapping = {
            'local': self.local,
            'remote': self.remote
        }

        results = {}

        for x in args.keys():
            if x in mapping:
                if args[x] is not False or str(args[x]) != 'False':
                    results[x] = mapping[x](args)
        return results

    def remote(self, args):

        methods = args['method']
        if len(methods) == 0:
            print("you did not specify any methods, we fetch all methods remotely now!")
            methods = self.cisClient.get_libraries()

        for method in methods:
            self.stasisClient.schedule_steac(method)

    def local(self, args):

        methods = args['method']

        if len(methods) == 0:
            print("you did not specify any methods, we fetch all methods remotely now!")
            methods = self.cisClient.get_libraries()

        if args['delay'] > 0:
            print(f"start got delayed by {args['delay']}s")
            sleep(args['delay'])

        print(f"we are running steac over these methods: {methods}")
        for method in methods:
            """
            start local processing
            """
            pass
            elevator = NodeEvaluator(self._secret)

            env = elevator.get_aws_env()

            springProfiles = elevator.optimize_profiles(args)

            print(f"generated spring profiles to activate: {springProfiles}")
            env['SPRING_PROFILES_ACTIVE'] = springProfiles

            for e in args['env']:
                env[e] = os.getenv(e)

            elevator.process_steac(
                client=elevator.buildClient(),
                config={"method": method},
                environment=env,
                message=None,
                queue_url=None,
                sqs=None,
                args=None
            )

    @staticmethod
    def configure_steac(main_parser, sub_parser):

        parser = sub_parser.add_parser(name="steac", help="provides steac interactions")

        parser.add_argument("-d", "--delay",
                            help="delay the start of this tool until the given time in seconds is ellapsed",
                            required=False, type=int, default=0)
        parser.add_argument("-m", "--method", help="this is the methods you want to run steac over",
                            required=False, action="append", default=[])

        parser.add_argument("--remote", help="this schedules the operation to the remote queue",
                            required=False, default=False, action="store_true")

        parser.add_argument("--local", help="this does the processing locally",
                            required=False, default=False, action="store_true")

        parser.add_argument("-a", "--add", help="add a profile to the calculation instructions", action="append",
                            required=False, default=[])

        parser.add_argument("-r", "--remove",
                            help="remove a profile from instructions. In case we don't want to use it right now",
                            action="append",
                            required=False, default=[])

        parser.add_argument("-e", "--env",
                            help="register this environment variable",
                            action="append", required=False, default=[])
        return parser
