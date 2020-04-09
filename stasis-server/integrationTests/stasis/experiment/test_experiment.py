import time

import requests
import simplejson as json

apiUrl = "https://test-api.metabolomics.us/stasis"
samplename = "test_%s" % str(time.time()).split('.')[-1]
delay = 1


def test_get_experiment_paged_default(api_token):
    result = requests.get(apiUrl + '/experiment/unknown', headers=api_token)
    data = json.loads(result.content)
    assert 25 == len(data['items'])


def test_get_experiment_paged_custom_page_size(api_token):
    result = requests.get(apiUrl + '/experiment/unknown/15', headers=api_token)
    data = json.loads(result.content)

    assert 15 == len(data['items'])
    assert data['last_item']['id'] == 'B2b_SA1594_TEDDYLipids_Neg_MSMS_1U2WN'


def test_get_experiment_paged_second_page(api_token):
    result = requests.get(apiUrl + '/experiment/unknown/15/B5_P20Lipid_Pos_NIST001', headers=api_token)
    if result.status_code != 200:
        print(result.text)
        data = {'items': []}
    else:
        data = json.loads(result.content)

    assert 7 <= len(data['items'])
