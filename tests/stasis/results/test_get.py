from stasis.route.route import processResultMessage
from stasis.results import get
import simplejson as json


def test_get(requireMocking):
    # store data

    jsonString = json.dumps(
        {
            'id': 'test',
            'sample': 'test',
            'time': 1525832496333,
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
    )
    print(jsonString)
    print("tada")
    assert processResultMessage(
        json.loads(
            jsonString
            , use_decimal=True
        )
    )

    # process data

    result = get.get({
        "pathParameters": {
            "sample": "test"
        }
    }, {})

    print(result)
    assert result['statusCode'] == 200
    assert 'body' in result
    assert json.loads(result['body'])["id"] == "test"
