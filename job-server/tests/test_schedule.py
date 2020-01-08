import os


def test_schedule(requireMocking):
    assert os.environ['aggregation_queue'] is not None
    assert os.environ['processing_queue'] is not None
