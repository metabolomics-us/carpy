from crag.aws import JobAggregator
from stasis_client.client import StasisClient

from lcb.evaluator import Evaluator


class AggregateEvaluator(Evaluator):
    """
    executes aggregations locally
    """

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
            JobAggregator(arguments).aggregate_job(job=args['remote'], upload=args['upload'])
