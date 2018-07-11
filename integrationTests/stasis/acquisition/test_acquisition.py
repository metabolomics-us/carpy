import time

import requests

apiUrl = "https://dev-api.metabolomics.us/stasis/acquisition"
samplename = 'test_%s' % time.time()


def test_create():
    data = {
        'sample': samplename,
        'experiment': 'mySecretExp',
        'acquisition': {
            'instrument': 'test inst',
            'ionisation': 'positive',
            'name': 'some name',
            'method': 'gcms'
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
            'comment': ''
        }
    }

    response = requests.post(apiUrl, json=data)
    print(response.reason)

    assert 200 == response.status_code
    time.sleep(1)

    response = requests.get(apiUrl + '/' + samplename)
    assert 200 == response.status_code

    sample = response.json()
    assert samplename == sample['sample']
    assert 'mySecretExp' == sample['experiment']
    assert all(x in sample.keys() for x in
               ['experiment', 'metadata', 'acquisition', 'sample', 'processing', 'time', 'id', 'userdata'])

    tracking_response = requests.get('https://dev-api.metabolomics.us/stasis/tracking/%s' % sample['id'])

    assert 200 == tracking_response.status_code
    tracking = tracking_response.json()
    assert 'entered' == tracking['status'][0]['value']
