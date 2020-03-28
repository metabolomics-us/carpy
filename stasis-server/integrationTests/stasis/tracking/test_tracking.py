import time

import requests
import simplejson as json

apiUrl = "https://test-api.metabolomics.us/stasis"
samplename = "test_%s" % str(time.time()).split('.')[-1]
delay = 1


def test_create(api_token):
    data = {
        'sample': samplename,
        'status': 'entered'
    }

    response = requests.post(apiUrl + '/tracking', json=data, headers=api_token)
    assert 200 == response.status_code
    time.sleep(delay)

    response = requests.get(apiUrl + '/tracking/' + samplename, headers=api_token)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    assert samplename == sample['sample']


def test_create_with_processed_state(api_token):
    data = {
        'sample': "dummy_{}".format(samplename),
        'status': 'processing'
    }

    response = requests.post(apiUrl + '/tracking', json=data, headers=api_token)
    print(response)
    assert 200 == response.status_code
    time.sleep(delay)

    response = requests.get(apiUrl + '/tracking/' + "dummy_{}".format(samplename), headers=api_token)
    assert 200 == response.status_code

    sample = json.loads(response.content)
    assert "dummy_{}".format(samplename) == sample['sample']
    print(sample)


def test_create_with_file_handle(api_token):
    data = {
        'sample': samplename,
        'status': 'entered',
        'fileHandle': samplename + ".mzml"
    }

    response = requests.post(apiUrl + '/tracking', json=data, headers=api_token)
    assert 200 == response.status_code
    time.sleep(delay)

    response = requests.get(apiUrl + '/tracking/' + samplename, headers=api_token)
    assert 200 == response.status_code

    sample = json.loads(response.content)

    assert samplename == sample['sample']
    assert "%s.mzml" % samplename == sample['status'][0]['fileHandle']


def test_create_not_merging_statuses(api_token):
    requests.delete(apiUrl + '/tracking/processed-sample', headers=api_token)
    data = [{'sample': 'processed-sample', 'status': 'entered'},
            {'sample': 'processed-sample', 'status': 'acquired'},
            {'sample': 'processed-sample', 'status': 'converted'},
            {'sample': 'processed-sample', 'status': 'scheduled'},
            {'sample': 'processed-sample', 'status': 'processing'},
            {'sample': 'processed-sample', 'status': 'deconvoluted'},
            {'sample': 'processed-sample', 'status': 'corrected'},
            {'sample': 'processed-sample', 'status': 'annotated'},
            {'sample': 'processed-sample', 'status': 'quantified'},
            {'sample': 'processed-sample', 'status': 'replaced'},
            {'sample': 'processed-sample', 'status': 'exported'}]

    result = None
    for d in data:
        requests.post(apiUrl + '/tracking', json=d, headers=api_token)
        time.sleep(delay)
        result = requests.get(apiUrl + '/tracking/processed-sample', headers=api_token)

    # requests.delete(apiUrl + '/tracking/processed-sample')

    assert 200 == result.status_code
    assert 'processed-sample' == result.json()['sample']
    assert 11 == len(result.json()['status'])
