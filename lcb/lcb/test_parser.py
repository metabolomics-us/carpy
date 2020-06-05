from pytest import fail

from lcb.parser import Parser


def test_parse_default_mapping(stasis_cli):
    try:
        parser = Parser(stasis_cli)
        parser.parse()
        fail()
    except SystemExit as e:
        pass


def test_parse_empty_mapping(stasis_cli):
    try:
        parser = Parser(stasis_cli, {})
        parser.parse([])
        fail()
    except KeyError:
        # expected error
        pass


def test_parse_job_mapping_empty(stasis_cli):
    def call(args):
        pass

    parser = Parser(stasis_cli, {
        "job": call,
        "sample": call,
        "aggregate": call
    })
    parser.parse([])


def test_parse_job_mapping_empty_job_specified(stasis_cli):
    def call(args):
        pass

    parser = Parser(stasis_cli, {
        "job": call,
        "sample": call,
        "aggregate": call
    })

    try:
        parser.parse(['job'])
        fail()
    except (SystemExit, Exception) as e:
        pass


def test_parse_job_mapping_job_id_specified(stasis_cli):
    def call(args):
        print(args)

    parser = Parser(stasis_cli, {
        "job": call,
        "sample": call,
        "aggregate": call
    })

    parser.parse(['job', '-i', 'test'])


def test_parse_no_arguments(stasis_cli):
    def call(args):
        print(args)

    parser = Parser(stasis_cli, {
        "job": call,
        "sample": call,
        "aggregate": call
    })

    try:
        parser.parse()
        fail()
    except SystemExit as e:
        pass
