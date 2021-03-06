import argparse

from cisclient.client import CISClient
from stasis_client.client import StasisClient

from lcb.aggregate_evaluator import AggregateEvaluator
from lcb.compound_evaluator import SteacEvaluator
from lcb.job_evaluator import JobEvaluator
from lcb.load_secrets import Secrets
from lcb.node_evaluator import NodeEvaluator
from lcb.sample_evaluator import SampleEvaluator


class Parser:
    """
    general command line parser
    """

    def __init__(self, mapping: dict = None):

        parser = argparse.ArgumentParser(prog="lcb")
        parser.add_argument("--config",
                            help="specifies your configuration to be used and override env variabls. Needs to be a *.yml file.",
                            required=False, default="env-default.yml",type=str)
        sub = parser.add_subparsers(help="this contains all the different scopes, available to LCB")

        if mapping is None:
            # registers the default mapping
            mapping = {
                'sample': SampleEvaluator().evaluate_command,
                'job': JobEvaluator().evaluate_command,
                'aggregate': AggregateEvaluator().evaluate_command,
                'node': NodeEvaluator().evaluate_command,
                'steac': SteacEvaluator().evaluate_command
            }

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

        secret = Secrets(config=result['config'])
        print(f"parsed: {result}")
        if len(result) == 0:
            self.parser.print_usage()
        elif 'func' in result:
            result['func'](secret, result)
        else:
            raise KeyError("you need to make sure that a 'func' is registered when you create the parser!")

    @staticmethod
    def configure_monitor(main_parser, sub_parser):
        """
        configures a monitor to track the state of calculations
        """
