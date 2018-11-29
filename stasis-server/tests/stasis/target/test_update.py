import simplejson as json

from stasis.target import create, get, update

jsonString = json.dumps({'method': 'test_lib', 'mz_rt': '12_1', 'name': 'unknown', 'sample': 'tgtTest'})
newStuff = json.dumps({'method': 'test_lib', 'mz_rt': '12_1', 'name': 'newStuff', 'sample': 'tgtTest'})


def test_update(requireMocking):
    response = create.create({'body': jsonString}, {})
    assert response['statusCode'] == 200
    tgt = json.loads(response['body'])
    assert 'unknown' == tgt['name']

    response = update.update({'body': newStuff}, {})

    print('response from update: %s' % response)
    assert 200 == response['statusCode']

    response = get.get({'pathParameters': {
        'method': 'test_lib',
        'mz_rt': '12_1'}
    }, {})
    print("NEW targets: %s " % json.loads(response['body'])['targets'])
    assert 200 == response['statusCode']
    updated = json.loads(response['body'])['targets'][0]
    print('updated: %s' % updated)
    assert 'tgtTest' == updated['sample']
    assert 'newStuff' == updated['name']


def test_missing_mzrt(requireMocking):
    result = update.update({
        'body': json.dumps({'name': 'blah', 'mz_rt': 'asd'})
    }, {})
    assert 422 == result['statusCode']


def test_missing_body(requireMocking):
    result = update.update({
        'body': json.dumps({'method': 'blah', 'sample': 'asd'})
    }, {})
    assert 422 == result['statusCode']


def test_update_inexistent_taget(requireMocking):
    result = update.update({
        'body': json.dumps({
            'method': 'notfound',
            'mz_rt': 'invalid',
            'name': 'newStuff',
            'sample': 'tgtTest'
        })
    }, {})
    assert 404 == result['statusCode']
