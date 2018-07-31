import time

import requests

tgtUrl = "https://dev-api.metabolomics.us/stasis/target"
apiUrl = "https://dev-api.metabolomics.us/stasis/library"
data = [
    {'method': 'test_lib | unknown | unknown | positive', 'mz_rt': '10_123', 'sample': 'sample1', 'name': 'unknown'},
    {'method': 'test_other | unknown | unknown | negative', 'mz_rt': '10_123', 'sample': 'sample1', 'name': 'newStuff'}]


def test_get():
    # post data
    [requests.post(tgtUrl, json=x) for x in data]

    # test
    response = requests.get(apiUrl)

    assert 200 == response.status_code
    items = response.json()
    print('libraries: %s' % items)
    assert len(items) == 2
    assert 'test_lib | unknown | unknown | positive' in items
    assert 'test_other | unknown | unknown | negative' in items

    time.sleep(1)
    # cleanup -- not working for some reason
    requests.delete('%s/%s/%s' % (tgtUrl, 'test_lib | unknown | unknown | positive', '10_123'))
    requests.delete('%s/%s/%s' % (tgtUrl, 'test_other | unknown | unknown | negative', '10_123'))
