import simplejson as json

from stasis.target import create, get


def test_create_success(requireMocking):
    jsonString = json.dumps({'method': 'test_lib', 'mz_rt': '12_1', 'sample': 'tgtTest'})

    response = create.create({'body': jsonString}, {})
    assert response['statusCode'] == 200

    result = get.get({'pathParameters': {
        'method': 'test_lib', 'mz_rt': '12_1'}
    }, {})

    assert 200 == result['statusCode']
    assert 'tgtTest' == json.loads(result['body'])['sample']
    assert '12' == json.loads(result['body'])['mz']
    assert '1' == json.loads(result['body'])['rt']


def test_create_invalid_data(requireMocking):
    jsonString = json.dumps(
        {'method': 'test_lib', 'sample': 'tgtTest', 'splash': 'splash10-a112-0123456789-a0s1d2f3g4h5j6k7l8q9'})

    result = create.create({'body': jsonString}, {})
    assert 422 == result['statusCode']
    assert 'body' in result
