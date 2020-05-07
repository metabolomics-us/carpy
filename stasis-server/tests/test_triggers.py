##
# this tests the
from pytest import fail

from stasis.bucket.triggers import bucket_json


def test_bucket_json_fail_wrong_file_handle(requireMocking):
    event = {
        'Records': [{
            's3': {
                'object': {
                    'key': 'test.gz'
                }
            }
        }
        ]
    }

    try:
        bucket_json(event, {})
        fail()
    except Exception as e:
        pass


def test_bucket_json(requireMocking, mocked_10_sample_job):
    event = {
        'Records': [{
            's3': {
                'object': {
                    'key': 'abc_5.mzml.json'
                }
            }
        }
        ]
    }

    bucket_json(event, {})
