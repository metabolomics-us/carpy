import argparse

from cisclient.client import CISClient
from stasis_client.client import StasisClient

from lcb.aggregate_evaluator import AggregateEvaluator
from lcb.compound_evaluator import SteacEvaluator
from lcb.job_evaluator import JobEvaluator
from lcb.node_evaluator import NodeEvaluator
from lcb.sample_evaluator import SampleEvaluator


class Parser:
    """
    general command line parser
    """

    def __init__(self, stasisClient: StasisClient, mapping: dict = None, cisClient: CISClient = None):
        parser = argparse.ArgumentParser(prog="lcb")
        parser.add_argument("--json", action="store_true", help="try to print everything as JSON")

        sub = parser.add_subparsers(help="this contains all the different scopes, available to LCB")

        if mapping is None:
            # registers the default mapping
            mapping = {
                'sample': SampleEvaluator(stasisClient).evaluate,
                'job': JobEvaluator(stasisClient).evaluate,
                'aggregate': AggregateEvaluator(stasisClient).evaluate,
                'node': NodeEvaluator(stasisClient).evaluate,
                'steac': SteacEvaluator(stasisClient, cisClient).evaluate
            }

        # TODO this needs to be more dynamic done over all the mappings
        jobs = JobEvaluator.configure_jobs(main_parser=parser, sub_parser=sub)
        self.configure(jobs, mapping)

        samples = SampleEvaluator.configure_samples(main_parser=parser, sub_parser=sub)
        self.configure(samples, mapping)

        aggregator = AggregateEvaluator.configure_aggregate(main_parser=parser, sub_parser=sub)
        self.configure(aggregator, mapping)

        node = NodeEvaluator.configure_node(main_parser=parser, sub_parser=sub)
        self.configure(node, mapping)

        steac = SteacEvaluator.configure_steac(main_parser=parser, sub_parser=sub)
        self.configure(steac, mapping)

        self.parser = parser

    def configure(self, parser, mapping):
        """
        associates the mapping with the job
        :param parser:
        :param mapping:
        :return:
        """
        key = parser.prog.replace("lcb", "").strip()
        try:

            parser.set_defaults(func=mapping[key])
        except KeyError as k:
            raise KeyError(f"sorry we did not find '{key}' in the configured mappings {mapping}")

    def parse(self, args=None):
        """
        does the actual parsing and calls the associated functions
        :return:
        """

        result = vars(self.parser.parse_args(args))

        print(f"parsed: {result}")
        if len(result) == 1:
            self.parser.print_usage()
        elif 'func' in result:
            result['func'](result)
        else:
            raise KeyError("you need to make sure that a 'func' is registered when you create the parser!")

    @staticmethod
    def configure_monitor(main_parser, sub_parser):
        """
        configures a monitor to track the state of calculations
        """
<<<<<<< HEAD
=======

    @staticmethod
    def configure_node(main_parser, sub_parser):

        parser = sub_parser.add_parser(name="node", help="starts a node for computations")

        parser.add_argument("-s", "--single", help="runs a single node", action="store_true",
                            required=True)
        return parser

    @staticmethod
    def configure_aggregate(main_parser, sub_parser):

        parser = sub_parser.add_parser(name="aggregate", help="local aggregation based operations")

        parser.add_argument("-r", "--remote", help="this is your remote job id, you would like to locally aggregate",
                            required=True)

        parser.add_argument("-s", "--store",
                            help="this is the directory where do you want to store the aggregated data", required=True,
                            type=str, default=False)

        parser.add_argument("-u", "--upload",
                            help="uploads the result to the remote buckets", required=False,
                            action="store_true", default=False)

        parser.add_argument("--zero-replacement", action='store_true', default=True, dest="zero_replacement")
        parser.add_argument("--mz-tolerance", default=0.01, type=float, dest="mz_tolerance")
        parser.add_argument("--rt-tolerance", default=0.1, type=float, dest="rt_tolerance")

        return parser

    @staticmethod
    def configure_jobs(main_parser, sub_parser):
        """
        configures all the options for handling of jobs
        :param jobs:
        :return:
        """

        parser = sub_parser.add_parser(name="job", help="job based operations")
        parser.add_argument("-i", "--id", help="this is your job id", required=True)

        parser.add_argument("-u", "--upload",
                            help="registers the specified job file in the system in preparation for processing. You steel need to start the processing",
                            type=str, default=False)
        parser.add_argument("-p", "--process",
                            help="this starts the processing of the specified job id in the remote system",
                            action='store_true')
        parser.add_argument("--wait-for", nargs='+',
                            help="which states we want to wait for.", dest='wait_for',
                            type=str, default=False)
        parser.add_argument("--wait-attempts",
                            help="how many attempts we do until we are done waiting for a job",
                            type=int, default=10000, dest='wait_attempts')
        parser.add_argument("--wait-time",
                            help="how long do we wait in seconds between attempts for the wait module",
                            type=int, default=10, dest='wait_time')

        parser.add_argument("-d", "--detail", help="specify this flag to return a detailed report",
                            action='store_true')
        parser.add_argument("-e", "--exist", help="checks if the given job exist", action='store_true')
        parser.add_argument("-s", "--status", help="specify this flag to return the current status",
                            action='store_true')
        parser.add_argument("-r", "--retrieve",
                            help="this downloads the specified job, if available to the specified directory..",
                            type=str, default=False)

        parser.add_argument("--force-sync",
                            help="forces a synchronization of the given job. In case stasis is hanging",
                            action='store_true', dest='force_sync')

        return parser

    @staticmethod
    def configure_samples(main_parser, sub_parser):
        """
        configures all the options for a sample parser
        :param sample_parser:
        :return:
        """

        parser = sub_parser.add_parser(name="sample", help="sample based operations")
        parser.add_argument("-i", "--id", help="this is your sample id or name", required=True)
        parser.add_argument("-s", "--status", help="specify this flag to return the current status",
                            action='store_true')
        parser.add_argument("-p", "--process", help="this starts the processing of the specified sample",
                            action='store_true')
        parser.add_argument("-r", "--retrieve", help="this downloads the specified sample result", action='store_true')
        parser.add_argument("-f", "--full",
                            help="this downloads the specified sample result and all associated metadata",
                            action='store_true')
        parser.add_argument("-e", "--exist", help="checks if the given sample exist", action='store_true')
        parser.add_argument("-d", "--detail", help="provides a complete detailed view of the sample",
                            action='store_true')
        parser.add_argument("--profile", help="which profile to utilize for scheduling", default="lcms", required=False)
        parser.add_argument("--env", help="which env to utilize for scheduling", default="test", required=False)

        return parser
>>>>>>> 02d08a26025fc67f2d633d5668f865573c1dfcfb
