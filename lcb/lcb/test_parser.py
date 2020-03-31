from pytest import fail

from lcb.parser import Parser


def test_parse_no_mapping():
    try:
        parser = Parser({})
        parser.parse({})
        fail()
    except KeyError:
        # expected error
        pass


def test_parse_job_mapping_empty():
    def call(args):
        pass

    parser = Parser({
        "job": call,
        "sample": call
    })
    parser.parse({})
