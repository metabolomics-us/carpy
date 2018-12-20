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


def test_get_experiment_paged_default(api_token):
    result = requests.get(apiUrl + '/experiment/unknown', headers=api_token)
    data = json.loads(result.content)

    assert 25 == len(data['items'])
    assert data['last_item']['id'] == 'BioRec_LipidsPos_PhIV_002'


def test_get_experiment_paged_custom_page_size(api_token):
    result = requests.get(apiUrl + '/experiment/12345/25', headers=api_token)
    data = json.loads(result.content)

    assert 25 == len(data['items'])
    assert data['last_item']['id'] == 'test1544735921246'


def test_get_experiment_paged_second_page(api_token):
    result = requests.get(apiUrl + '/experiment/12345/25/test1544801381510', headers=api_token)
    if result.status_code != 200:
        print(result.text)
        data = {'items': []}
    else:
        data = json.loads(result.content)

    assert 7 <= len(data['items'])
    # new last_item
    assert 'last_item' not in data
