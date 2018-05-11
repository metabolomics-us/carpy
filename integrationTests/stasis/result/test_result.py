import simplejson as json
import time
import requests

from stasis.acquisition import create

apiUrl = "https://test-api.metabolomics.us/stasis/result"
samplename = f'test_{time.time()}'


def test_create():
    data = {
        'sample': samplename,
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
        'injections': {
            'test_1': {
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

    response = requests.post(apiUrl, json=data)
    assert 200 == response.status_code

    time.sleep(5)

    response = requests.get(apiUrl + '/' + samplename)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    assert samplename == sample['sample']
