import time

import requests
import simplejson as json

apiUrl = "https://test-api.metabolomics.us/stasis"
samplename = "test_%s" % str(time.time()).split('.')[-1]
delay = 1


def test_get_experiment_paged_default(api_token):
    result = requests.get(apiUrl + '/experiment/unknown', headers=api_token)
    data = json.loads(result.content)

    print(api_token)
    print(json.dumps(data, indent=2))

    assert 25 == len(data['items'])


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
