from crag.aws import JobAggregator
from stasis_client.client import StasisClient

from lcb.evaluator import Evaluator


class AggregateEvaluator(Evaluator):
    """
    executes aggregations locally
    """

    def __init__(self, stasis: StasisClient):
        super().__init__(stasis)

    def evaluate(self, args: dict):
        mapping = {
            'remote': self.remote_data,
        }

        results = {}

        for x in args.keys():
            if x in mapping:
                if args[x] is not False or str(args[x]) != 'False':
                    results[x] = mapping[x](args)
        return results

    def remote_data(self, args):

        if args['remote'] == '*':
            print("aggregating all known jobs")
            raise Exception("todo!!!")
        else:
            arguments = {
                'job': args['remote'],
                'zero_replacement': args['zero_replacement'],
                'upload': args['upload'],
                'mz_tolerance': args['mz_tolerance'],
                'rt_tolerance': args['rt_tolerance'],
            }
<<<<<<< HEAD
            JobAggregator(arguments).aggregate_job(job=args['remote'], upload=False)

    @staticmethod
    def configure_aggregate(main_parser, sub_parser):

        parser = sub_parser.add_parser(name="aggregate", help="local aggregation based operations")

        parser.add_argument("-r", "--remote", help="this is your remote job id, you would like to locally aggregate",
                            required=True)

        parser.add_argument("-s", "--store",
                            help="this is the directory where do you want to store the aggregated data", required=True,
                            type=str, default=False)

        parser.add_argument("--zero-replacement", action='store_true', default=True, dest="zero_replacement")
        parser.add_argument("--mz-tolerance", default=0.01, type=float, dest="mz_tolerance")
        parser.add_argument("--rt-tolerance", default=0.1, type=float, dest="rt_tolerance")

        return parser
=======
            JobAggregator(arguments).aggregate_job(job=args['remote'], upload=args['upload'])
>>>>>>> 02d08a26025fc67f2d633d5668f865573c1dfcfb
