import time

import pytest
import requests

apiUrl = "https://test-api.metabolomics.us/stasis/acquisition"


@pytest.mark.parametrize("samples", [1, 10, 25])
def test_create(samples, api_token):
    _samplename = 'test_%s' % time.time()
    for sample in range(0, samples):
        samplename = "{}_{}".format(_samplename, sample)

        response = _upload_test_sample(samplename, samples, api_token)

        assert 200 == response.status_code
        #        time.sleep(1)

        response = requests.get(apiUrl + '/' + samplename, headers=api_token)
        assert 200 == response.status_code

        sample = response.json()
        assert samplename == sample['sample']
        assert 'mySecretExp_{}'.format(samples) == sample['experiment']
        assert all(x in sample.keys() for x in
                   ['experiment', 'metadata', 'acquisition', 'sample', 'processing', 'time', 'id', 'userdata'])

        tracking_response = requests.get('https://test-api.metabolomics.us/stasis/tracking/%s' % sample['id'],
                                         headers=api_token)

        assert 200 == tracking_response.status_code
        tracking = tracking_response.json()
        assert 'entered' == tracking['status'][0]['value']



@pytest.mark.parametrize("samples", [1, 10, 25])
def test_just_create(samples, api_token):
    for sample in range(0,samples):
        _upload_test_sample(samplename="test", samples=samples, api_token=api_token)


def _upload_test_sample(samplename, samples, api_token):
    data = {
        'sample': samplename,
        'experiment': 'mySecretExp_{}'.format(samples),
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
    response = requests.post(apiUrl, json=data, headers=api_token)
    return response
