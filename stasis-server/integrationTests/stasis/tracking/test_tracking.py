import time

import requests
import simplejson as json

apiUrl = "https://test-api.metabolomics.us/stasis"
samplename = "test_%s" % str(time.time())
delay = 1


def test_create(api_token):
    data = {
        'sample': samplename,
        'status': 'entered'
    }

    print(data)
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
            {'sample': 'processed-sample', 'status': 'acquired', 'fileHandle': 'processed-sample.d'},
            {'sample': 'processed-sample', 'status': 'converted', 'fileHandle': 'processed-sample.mzml'},
            {'sample': 'processed-sample', 'status': 'scheduled', 'fileHandle': 'processed-sample.mzml'},
            {'sample': 'processed-sample', 'status': 'processing', 'fileHandle': 'processed-sample.mzml'},
            {'sample': 'processed-sample', 'status': 'deconvoluted', 'fileHandle': 'processed-sample.mzml'},
            {'sample': 'processed-sample', 'status': 'corrected', 'fileHandle': 'processed-sample.mzml'},
            {'sample': 'processed-sample', 'status': 'annotated', 'fileHandle': 'processed-sample.mzml'},
            {'sample': 'processed-sample', 'status': 'quantified', 'fileHandle': 'processed-sample.mzml'},
            {'sample': 'processed-sample', 'status': 'replaced', 'fileHandle': 'processed-sample.mzml'},
            {'sample': 'processed-sample', 'status': 'exported', 'fileHandle': 'processed-sample.mzml.json'}]

    result = None
    for d in data:
        requests.post(apiUrl + '/tracking', json=d, headers=api_token)
        time.sleep(delay)
        result = requests.get(apiUrl + '/tracking/processed-sample', headers=api_token)

    # requests.delete(apiUrl + '/tracking/processed-sample')

    assert 200 == result.status_code
    assert 'processed-sample' == result.json()['sample']
    assert 11 == len(result.json()['status'])

    result_data = result.json()['status']

    assert 'fileHandle' not in result_data[0]
    assert 'fileHandle' in result_data[1]
    assert 'fileHandle' in result_data[2]
    assert 'fileHandle' in result_data[3]
    assert 'fileHandle' in result_data[4]
    assert 'fileHandle' in result_data[5]
    assert 'fileHandle' in result_data[6]
    assert 'fileHandle' in result_data[7]
    assert 'fileHandle' in result_data[8]
    assert 'fileHandle' in result_data[9]
    assert 'fileHandle' in result_data[10]

    assert result_data[1]['fileHandle'] == 'processed-sample.d'
    assert result_data[2]['fileHandle'] == 'processed-sample.mzml'
    assert result_data[3]['fileHandle'] == 'processed-sample.mzml'
    assert result_data[4]['fileHandle'] == 'processed-sample.mzml'
    assert result_data[5]['fileHandle'] == 'processed-sample.mzml'
    assert result_data[6]['fileHandle'] == 'processed-sample.mzml'
    assert result_data[7]['fileHandle'] == 'processed-sample.mzml'
    assert result_data[8]['fileHandle'] == 'processed-sample.mzml'
    assert result_data[9]['fileHandle'] == 'processed-sample.mzml'
    assert result_data[10]['fileHandle'] == 'processed-sample.mzml.json'
