import time

import requests

tgtUrl = "https://test-api.metabolomics.us/stasis/target"
apiUrl = "https://test-api.metabolomics.us/stasis/library"
data = [
    {'method': 'test_lib | unknown | unknown | positive', 'mz_rt': '10_123', 'sample': 'sample1', 'name': 'unknown'},
    {'method': 'test_other | unknown | unknown | negative', 'mz_rt': '10_123', 'sample': 'sample1', 'name': 'newStuff'}]


def test_get(api_token):
    # post data
    [requests.post(tgtUrl, json=x, headers=api_token) for x in data]

    # test
    response = requests.get(apiUrl, headers=api_token)

    assert 200 == response.status_code
    items = response.json()
    print('libraries: %s' % '\n'.join(items))

    assert len(items) >= 2
    assert 'test_lib | unknown | unknown | positive' in items
    assert 'test_other | unknown | unknown | negative' in items

    time.sleep(1)

    # cleanup -- not working for some reason
    requests.delete('%s/%s/%s' % (tgtUrl, 'test_lib | unknown | unknown | positive', '10_123'), headers=api_token)
    requests.delete('%s/%s/%s' % (tgtUrl, 'test_other | unknown | unknown | negative', '10_123'), headers=api_token)
