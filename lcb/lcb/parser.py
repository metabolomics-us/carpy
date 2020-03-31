import argparse


class Parser:
    """
    general command line parser
    """

    def __init__(self, mapping: dict):
        parser = argparse.ArgumentParser(prog="lcb")
        sub = parser.add_subparsers(help="this contains all the different scopes, available to LCB")

        jobs = self.configure_jobs(main_parser=parser, sub_parser=sub)
        job_parser_name_ = jobs.prog.replace(parser.prog, "").strip()
        jobs.set_defaults(func=mapping.get(job_parser_name_))

        samples = self.configure_samples(main_parser=parser, sub_parser=sub)
        samples.set_defaults(func=mapping[samples.prog.replace(parser.prog, "").strip()])
        self.parser = parser

    def parse(self, args) -> argparse.Namespace:
        """
        does the actual parsing and returns a namespace object.
        :return:
        """

        return self.parser.parse_args(args)

    def configure_jobs(self, main_parser, sub_parser):
        """
        configures all the options for handling of jobs
        :param jobs:
        :return:
        """

        jobs = sub_parser.add_parser(name="job", help="job based operations")

        return jobs

    def configure_samples(self, main_parser, sub_parser):
        """
        configures all the options for a sample parser
        :param sample_parser:
        :return:
        """

        samples = sub_parser.add_parser(name="sample", help="sample based operations")

        return samples
