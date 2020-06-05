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

        arguments = {
            'job': args['remote'],
            'zero_replacement': args['zero_replacement'],
            'upload': False,
            'mz_tolerance': args['mz_tolerance'],
            'rt_tolerance': args['rt_tolerance'],
        }
        JobAggregator(arguments).aggregate_job(job=args['remote'], upload=False)
