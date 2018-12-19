import time

import requests
import simplejson as json

apiUrl = "https://test-api.metabolomics.us/stasis/file"


def test_exists(api_token):
    response = requests.get(apiUrl + '/exists/test', headers=api_token)
    assert 200 == response.status_code
    assert 'test' == json.loads(response.content)['file']
    assert False == json.loads(response.content)['exist']
