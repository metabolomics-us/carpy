import simplejson as json

from stasis.target import create, get


def test_create_success(requireMocking):
    jsonString = json.dumps({'method': 'test_lib | unknown | unknown | positive',
                             'mz': 12.45, 'rt': 1.01, 'sample': 'tgtTest'})

    response = create.create({'body': jsonString}, {})
    assert response['statusCode'] == 200

    result = get.get({'pathParameters': {
        'method': 'test_lib | unknown | unknown | positive'}
    }, {})

    assert 200 == result['statusCode']
    added = json.loads(result['body'])['targets'][0]
    assert added['sample'] == 'tgtTest'
    assert added['mz'] == 12.45
    assert added['rt'] == 1.01
    assert added['mz_rt'] == '12.45_1.01'


def test_create_invalid_data(requireMocking):
    jsonString = json.dumps(
        {'method': 'test_lib | unknown | unknown | positive', 'sample': 'tgtTest'})

    result = create.create({'body': jsonString}, {})
    assert 422 == result['statusCode']
    print("body: " + json.dumps(result, indent=2))
    assert 'body' in result
    assert result['body'] == '{"error": "\'mz\' is a required property"}'
