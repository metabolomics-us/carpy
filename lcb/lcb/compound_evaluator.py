from cisclient.client import CISClient
from crag.aws import JobAggregator
from stasis_client.client import StasisClient

from lcb.evaluator import Evaluator
from lcb.node_evaluator import NodeEvaluator


class SteacEvaluator(Evaluator):
    """
    executes aggregations locally
    """

    def __init__(self, stasis: StasisClient, cis: CISClient):
        super().__init__(stasis)
        self.cis = cis

    def evaluate(self, args: dict):
        mapping = {
            'local': self.local,
        }

        results = {}

        for x in args.keys():
            if x in mapping:
                if args[x] is not False or str(args[x]) != 'False':
                    results[x] = mapping[x](args)
        return results

    def local(self, args):

        methods = args['method']

        if len(methods) == 0:
            print("you did not specify any methods, we fetch all methods remotely now!")
            methods = self.cis.get_libraries()

        print(f"we are running steac over these methods: {methods}")
        for method in methods:
            """
            start local processing
            """
            pass
            elevator = NodeEvaluator(self.client)

            env = elevator.get_aws_env()
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

        parser.add_argument("-m", "--method", help="this is the method you want to run steac",
                            required=False, action="append", default=[])

        parser.add_argument("-l", "--local", help="this is the method you want to run steac",
                            required=False, default=False, action="store_true")

        return parser
