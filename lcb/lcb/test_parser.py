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
    try:
        parser.parse({})
        fail()
    except KeyError as e:
        pass


def test_parse_job_mapping_empty_job_specified():
    def call(args):
        pass

    parser = Parser({
        "job": call,
        "sample": call
    })

    try:
        parser.parse(['job'])
        fail()
    except (SystemExit, Exception) as e:
        pass


def test_parse_job_mapping_job_id_specified():
    def call(args):
        print(args)

    parser = Parser({
        "job": call,
        "sample": call
    })

    parser.parse(['job', '-i', 'test'])


