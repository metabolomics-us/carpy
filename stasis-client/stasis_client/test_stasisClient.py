from time import time

from stasis_client.client import StasisClient

url = "https://dev-api.metabolomics.us/stasis"
key = "0anM2Bz9tI3Iyw9zZSpXLFBRb5EitCa2iPhd7O31"

client = StasisClient(url, key)


def test_sample_acquisition_create():
    data = _create_sample()
    result = client.sample_acquisition_create(data)

    print(result)

    assert result.status_code == 200

    result = client.sample_acquisition_get(data['sample'])

    print(result)

    assert result['sample'] == data['sample']


def _create_sample(name: str = "test"):
    data = {
        'sample': "123-{}-{}".format(name, time()),
        'experiment': 'mySecretExp_{}'.format(123),
        'acquisition': {
            'instrument': 'test inst',
            'ionisation': 'positive',
            'name': 'some name',
            'method': 'gcms'
        },
        'processing': {
            'method': 'gcms'
        },
        'metadata': {
            'class': '12345',
            'species': 'alien',
            'organ': 'honker'
        },
        'userdata': {
            'label': 'filexxx',
            'comment': ''
        }
    }
    return data


def test_sample_state():
    sample = _create_sample("123")
    result = client.sample_state_update(sample['sample'], "entered")

    print(result)
    assert client.sample_state(sample['sample'])[0]['value'] == "entered"


def test_sample_result():
    result = client.sample_result("Zeki_SIMVA_test_1uL.mzml")
    print(result)


