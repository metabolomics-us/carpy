import simplejson as json
import time
import requests

from stasis.acquisition import create


apiUrl = "https://test-api.metabolomics.us/stasis/tracking"
samplename = f'test_{time.time()}'

def test_create():
    data = {
            'sample': samplename,
            'status': 'entered'
        }


    response = requests.post(apiUrl, json=data)
    assert 200 == response.status_code

    time.sleep(5)

    response = requests.get(apiUrl+'/'+samplename)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    assert samplename == sample['sample']
