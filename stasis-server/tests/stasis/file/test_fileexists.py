import os
import simplejson as json

from stasis.file import exists
from stasis.service.Bucket import Bucket


def test_get(requireMocking):
    # test inexistent file
    event = {
        "pathParameters": {
            "sample": "test"
        }
    }

    result = exists.exists(event, {})

    print(json.dumps(result, indent=2))

    assert 200 == result['statusCode']
    assert False == json.loads(result['body'])['exist']
    assert 'test' == json.loads(result['body'])['file']

    # test existing file
    data_carrot = Bucket(os.environ['dataBucket'])
    data_carrot.save('test', 'blah')

    result = exists.exists(event, {})

    print(json.dumps(result, indent=2))

    assert 200 == result['statusCode']
    assert True == json.loads(result['body'])['exist']
    assert 'test' == json.loads(result['body'])['file']
