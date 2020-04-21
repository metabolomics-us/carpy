import argparse

from stasis_client.client import StasisClient

from lcb.job_evaluator import JobEvaluator
from lcb.sample_evaluator import SampleEvaluator


class Parser:
    """
    general command line parser
    """

    def __init__(self, stasisClient: StasisClient, mapping: dict = None):
        parser = argparse.ArgumentParser(prog="lcb")
        parser.add_argument("--json", action="store_true", help="try to print everything as JSON")

        sub = parser.add_subparsers(help="this contains all the different scopes, available to LCB")

        if mapping is None:
            # registers the default mapping
            mapping = {
                'sample': SampleEvaluator(stasisClient).evaluate,
                'job': JobEvaluator(stasisClient).evaluate
            }

        jobs = self.configure_jobs(main_parser=parser, sub_parser=sub)
        jobs.set_defaults(func=mapping.get(jobs.prog.replace(parser.prog, "").strip()))

        samples = self.configure_samples(main_parser=parser, sub_parser=sub)
        samples.set_defaults(func=mapping[samples.prog.replace(parser.prog, "").strip()])

        self.parser = parser

    def parse(self, args=None):
        """
        does the actual parsing and calls the associated functions
        :return:
        """

        result = vars(self.parser.parse_args(args))

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

    @staticmethod
    def configure_jobs(main_parser, sub_parser):
        """
        configures all the options for handling of jobs
        :param jobs:
        :return:
        """

        parser = sub_parser.add_parser(name="job", help="job based operations")
        parser.add_argument("-i", "--id", help="this is your job id", required=True)
        parser.add_argument("-s", "--status", help="specify this flag to return the current status",
                            action='store_true')

        parser.add_argument("-p", "--process",
                            help="this starts the processing of the specified job id in the remote system",
                            action='store_true')
        parser.add_argument("-a", "--aggregate", help="this aggregates the specified job locally", action='store_true')
        parser.add_argument("-r", "--retrieve", help="this downloads the specified job, if available",
                            action='store_true')
        parser.add_argument("-e", "--exist", help="checks if the given job exist", action='store_true')
        parser.add_argument("-u", "--upload",
                            help="registers the specified job file in the system in preparation for processing. You steel need to start the processing",
                            type=str)

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
