import time

import requests
import simplejson as json

apiUrl = "https://dev-api.metabolomics.us/stasis/acquisition"
samplename = 'test_%s' % time.time()


def test_create():
    data = {
        'sample': samplename,
        'experiment': 'mySecretExp',
        'acquisition': {
            'instrument': 'test inst',
            'ionisation': 'positive',  # psotivie || negative
            'method': 'gcms'  # gcms || lcms
        },
        'processing': {
            'method': 'gcms'
        },
        'metadata': {
            'class': '12345',
            'species': 'alien',
            'organ': 'honker'
        },
        'userdata': {
            'label': 'filexxx',
            'comment': '',
        },
    }

    response = requests.post(apiUrl, json=data)

    assert 200 == response.status_code

    time.sleep(5)

    response = requests.get(apiUrl + '/' + samplename)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    assert samplename == sample['sample']
