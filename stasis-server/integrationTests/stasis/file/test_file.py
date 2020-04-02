import requests

apiUrl = "https://test-api.metabolomics.us/stasis/file"


def test_exists_false(api_token):
    response = requests.head(apiUrl + '/test_im_not_real', headers=api_token)
    assert 404 == response.status_code


def test_exists(api_token):
    response = requests.head(apiUrl + '/test_data_pos.mzml', headers=api_token)
    assert 200 == response.status_code
