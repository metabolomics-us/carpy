import time

import requests
import simplejson as json

apiUrl = "https://test-api.metabolomics.us/stasis"
samplename = 'test_%s' % time.time()


def test_create():
    data = {
        'sample': samplename,
        'status': 'entered'
    }

    response = requests.post(apiUrl + '/tracking/', json=data)
    assert 200 == response.status_code

    time.sleep(15)

    response = requests.get(apiUrl + '/tracking/' + samplename)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    assert samplename == sample['sample']


def test_create_with_file_handle():
    data = {
        'sample': samplename,
        'status': 'entered',
        'fileHandle': samplename
    }

    response = requests.post(apiUrl + '/tracking', json=data)
    assert 200 == response.status_code

    time.sleep(15)

    response = requests.get(apiUrl + '/tracking/' + samplename)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    print("sample: %s" % sample)
    assert samplename == sample['sample']
    assert samplename == sample['status'][0]['fileHandle']


def test_get_experiment():
    # start prepare test data
    acq_data = [{
        'sample': 'test-query-experiment',
        'experiment': '1',
        'acquisition': {
            'instrument': 'flute',
            'name': 'method blah',
            'ionisation': 'positive',
            'method': 'lcms'
        },
        'processing': {
            'method': 'lcms'
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
    }, {
        'sample': 'test-query-experiment2',
        'experiment': '1',
        'acquisition': {
            'instrument': 'flute',
            'name': 'method blah',
            'ionisation': 'positive',
            'method': 'lcms'
        },
        'processing': {
            'method': 'lcms'
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
    }]
    acq = [requests.post(apiUrl + '/acquisition', json=ac) for ac in acq_data]
    assert 200 == acq[-1].status_code

    tracking_data = [{
        'sample': 'test-query-experiment',
        'status': 'entered',
        'fileHandle': 'test.mzml'
    }, {
        'sample': 'test-query-experiment2',
        'status': 'entered',
        'fileHandle': 'test2.mzml'
    }]
    trk = [requests.post(apiUrl + '/tracking', json=td) for td in tracking_data]
    assert 200 == trk[-1].status_code
    # end prepare test data

    result = requests.get(apiUrl + '/experiment/1')
    print(result.text)

    assert 200 == result.status_code
    assert 2 == len(json.loads(result.text))
