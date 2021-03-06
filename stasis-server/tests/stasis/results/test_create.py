import time

import simplejson as json

from stasis.results import create


def test_create_success(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps(
        {
            'sample': 'test',
            'time': 1525832496333,
            'injections': {
                'test_1': {
                    'logid':'1234',
                    'correction': {
                        'polynomial': 5,
                        'sampleUsed': 'test',
                        'curve': [
                            {
                                'x': 121.12,
                                'y': 121.2
                            },
                            {
                                'x': 123.12,
                                'y': 123.2
                            }
                        ]
                    },
                    'results': [
                        {
                            'target': {
                                'retentionIndex': 121.12,
                                'name': 'test',
                                'id': 'test_id',
                                'mass': 12.2
                            },
                            'annotation': {
                                'retentionIndex': 121.2,
                                'intensity': 10.0,
                                'replaced': False,
                                'mass': 12.2
                            }
                        },
                        {
                            'target': {
                                'retentionIndex': 123.12,
                                'name': 'test2',
                                'id': 'test_id2',
                                'mass': 132.12
                            },
                            'annotation': {
                                'retentionIndex': 123.2,
                                'intensity': 103.0,
                                'replaced': True,
                                'mass': 132.12
                            }
                        }
                    ]
                }
            }
        }
    )

    response = create.create({'body': jsonString}, {})
    print('RESPONSE: %s' % response)
    assert 'isBase64Encoded'in response
    assert 200 == response['statusCode']

    print("BODY: %s" % response['body'])

    assert 'test' == json.loads(response['body'])['sample']
    assert 5 == json.loads(response['body'])['injections']['test_1']['correction']['polynomial']
