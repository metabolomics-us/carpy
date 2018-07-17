import requests

apiUrl = "https://dev-api.metabolomics.us/stasis/target"


def test_get_create():
    data = {'method': 'test_lib', 'mz_rt': '10_123', 'sample': 'sample1'}
    response = requests.post(apiUrl, json=data)

    assert 200 == response.status_code


def test_get_without_mzrt():
    response = requests.get('%s/test_lib' % apiUrl)

    assert 200 == response.status_code
    item = response.json()
    assert 'test_lib' == item[0]['method']
    assert '10_123' == item[0]['mz_rt']
    assert '10' == item[0]['mz']
    assert '123' == item[0]['rt']


def test_get_with_mzrt():
    response = requests.get('%s/test_lib/10_123' % apiUrl)

    assert 200 == response.status_code
    item = response.json()
    assert 'test_lib' == item[0]['method']
    assert '10_123' == item[0]['mz_rt']
    assert '10' == item[0]['mz']
    assert '123' == item[0]['rt']
