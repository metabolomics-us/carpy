import time

import requests
import simplejson as json
from pytest import fail

apiUrl = "https://test-api.metabolomics.us/stasis/result"
samplename = f'test_{time.time()}'


def test_create(api_token):
    print(samplename)
    data = {
        'sample': samplename,
        'injections': {
            'test_1': {
                'logid': '1234',
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

    response = requests.post(apiUrl, json=data, headers=api_token)
    assert 200 == response.status_code

    time.sleep(5)

    response = requests.get(apiUrl + '/' + samplename, headers=api_token)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    assert samplename == sample['sample']

    response = requests.head(apiUrl + '/' + samplename, headers=api_token)
    assert 200 == response.status_code


def test_exists_false(api_token):
    response = requests.head(apiUrl + '/i_dont_exist' + samplename, headers=api_token)
    assert 404 == response.status_code