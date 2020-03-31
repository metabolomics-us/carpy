import argparse


class Parser:
    """
    general command line parser
    """

    def __init__(self, mapping: dict):
        parser = argparse.ArgumentParser(prog="lcb")
        sub = parser.add_subparsers(help="this contains all the different scopes, available to LCB")

        jobs = self.configure_jobs(main_parser=parser, sub_parser=sub)
        jobs.set_defaults(func=mapping.get(jobs.prog.replace(parser.prog, "").strip()))

        samples = self.configure_samples(main_parser=parser, sub_parser=sub)
        samples.set_defaults(func=mapping[samples.prog.replace(parser.prog, "").strip()])

        self.parser = parser

    def parse(self, args):
        """
        does the actual parsing and calls the associated functions
        :return:
        """

        result = vars(self.parser.parse_args(args))

        if 'func' in result:
            result['func'](result)
        else:
            raise KeyError("you need to make sure that a 'func' is registered when you create the parser!")

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
        parser.add_argument("-d", "--download", help="this downloads the specified job, if available",
                            action='store_true')
        parser.add_argument("-e", "--exist", help="checks if the given job exist", action='store_true')
        parser.add_argument("-r", "--register", help="registers the specified job file in the system", type=str)

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
        parser.add_argument("-d", "--download", help="this downloads the specified sample result", action='store_true')
        parser.add_argument("-e", "--exist", help="checks if the given sample exist", action='store_true')

        return parser
