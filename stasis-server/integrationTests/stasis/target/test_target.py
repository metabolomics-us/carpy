import requests

apiUrl = "https://test-api.metabolomics.us/stasis/target"
data = {'method': 'test_lib | unknown | unknown | positive',
        'mz': 10, 'rt': 123, 'sample': 'sample1', 'name': 'Unknown'}
data2 = {'method': 'test_del | unknown | unknown | positive',
         'mz': 1, 'rt': 2, 'mz_rt': '1_2', 'sample': 'sample1', 'name': 'unknown'}
newData = {'method': 'test_lib | unknown | unknown | positive',
           'mz_rt': '10_123', 'mz': 10, 'rt': 123, 'sample': 'sample1', 'name': 'newStuff'}


def test_create(api_token):
    response = requests.post(apiUrl, json=data, headers=api_token)

    assert 200 == response.status_code


def test_get_without_mzrt(api_token):
    response = requests.get('%s/test_lib | unknown | unknown | positive' % apiUrl, headers=api_token)

    assert 200 == response.status_code
    item = response.json()['targets']
    assert 'test_lib | unknown | unknown | positive' == item[0]['method']
    assert '10_123' == item[0]['mz_rt']
    assert 10 == item[0]['mz']
    assert 123 == item[0]['rt']


def test_update_success(api_token):
    response = requests.put(apiUrl, json=newData, headers=api_token)
    assert 200 == response.status_code
    item = response.json()
    assert 'newStuff' == item['name']


def test_update_missing_body(api_token):
    assert 422 == requests.put(apiUrl, headers=api_token).status_code


def test_update_empty_body(api_token):
    assert 422 == requests.put(apiUrl, json={}, headers=api_token).status_code


def test_delete(api_token):
    response = requests.post(apiUrl, json=data2, headers=api_token)
    assert 200 == response.status_code

    assert 204 == requests.delete(apiUrl + '/test_del | unknown | unknown | positive/1_2',
                                  headers=api_token).status_code
