import time
from pprint import pprint

import requests
import simplejson as json

apiUrl = "https://test-api.metabolomics.us/stasis"
samplename = "test_%s" % str(time.time()).split('.')[-1]
delay = 1


def test_get_experiment_paged_default(api_token):
    result = requests.get(apiUrl + '/experiment/none', headers=api_token)
    data = json.loads(result.content)
    assert 18 == len(data['items'])

def test_get_experiment_paged_second_page(api_token):
    result = requests.get(apiUrl + '/experiment/unknown/15/B5_P20Lipid_Pos_NIST001', headers=api_token)
    if result.status_code != 200:
        print(result.text)
        data = {'items': []}
    else:
        data = json.loads(result.content)
        pprint(data, indent=2)

    assert 7 <= len(data['items'])
