import requests

apiUrl = "https://dev-api.metabolomics.us/stasis/target"
data = {'method': 'test_lib', 'mz_rt': '10_123', 'sample': 'sample1', 'name': 'unknown'}
data2 = {'method': 'test_del', 'mz_rt': '1_2', 'sample': 'sample1', 'name': 'unknown'}
newData = {'method': 'test_lib', 'mz_rt': '10_123', 'sample': 'sample1', 'name': 'newStuff'}


def test_create():
    response = requests.post(apiUrl, json=data)

    assert 200 == response.status_code


def test_get_without_mzrt():
    response = requests.get('%s/test_lib' % apiUrl)

    assert 200 == response.status_code
    item = response.json()['targets']
    assert 'test_lib' == item[0]['method']
    assert '10_123' == item[0]['mz_rt']
    assert '10' == item[0]['mz']
    assert '123' == item[0]['rt']


def test_get_with_mzrt():
    response = requests.get('%s/test_lib/10_123' % apiUrl)

    assert 200 == response.status_code
    item = response.json()['targets']
    assert 'test_lib' == item[0]['method']
    assert '10_123' == item[0]['mz_rt']
    assert '10' == item[0]['mz']
    assert '123' == item[0]['rt']


def test_update_success():
    response = requests.put(apiUrl, json=newData)
    print("RESPONSE: %s" % response.text)
    assert 200 == response.status_code
    item = response.json()
    assert 'newStuff' == item['name']


def test_update_missing_body():
    assert 422 == requests.put(apiUrl).status_code


def test_update_empty_body():
    assert 422 == requests.put(apiUrl, json={}).status_code


def test_delete():
    response = requests.post(apiUrl, json=data2)
    assert 200 == response.status_code

    assert 204 == requests.delete('%s/%s/%s' % (apiUrl, 'test_del', '1_2')).status_code
