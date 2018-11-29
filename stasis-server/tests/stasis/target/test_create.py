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
    added = json.loads(result['body'])['targets'][0]
    assert 'tgtTest' == added['sample']
    assert '12' == added['mz']
    assert '1' == added['rt']


def test_create_invalid_data(requireMocking):
    jsonString = json.dumps(
        {'method': 'test_lib', 'sample': 'tgtTest'})

    result = create.create({'body': jsonString}, {})
    assert 422 == result['statusCode']
    assert 'body' in result
