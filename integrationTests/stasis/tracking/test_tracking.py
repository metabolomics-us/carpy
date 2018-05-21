import time

import requests
import simplejson as json

apiUrl = "https://test-api.metabolomics.us/stasis/tracking"
samplename = f'test_{time.time()}'

def test_create():
    data = {
            'sample': samplename,
            'status': 'entered'
        }


    response = requests.post(apiUrl, json=data)
    assert 200 == response.status_code

    time.sleep(15)

    response = requests.get(apiUrl+'/'+samplename)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    assert samplename == sample['sample']


def test_create_with_fileHandle():
    data = {
        'sample': samplename,
        'status': 'entered',
        'fileHandle': samplename
    }

    response = requests.post(apiUrl, json=data)
    assert 200 == response.status_code

    time.sleep(15)

    response = requests.get(apiUrl + '/' + samplename)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    assert samplename == sample['sample']
    assert samplename == sample['fileHandle']
