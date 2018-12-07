from time import time

from stasis_client.client import StasisClient

url = "https://dev-api.metabolomics.us/stasis"
key = "0anM2Bz9tI3Iyw9zZSpXLFBRb5EitCa2iPhd7O31"

client = StasisClient(url, key)


def test_sample_acquisition_create():
    data = {
        'sample': "123-test-{}".format(time()),
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
    result = client.sample_acquisition_create(data)

    print(result)

    assert result.status_code == 200

    result = client.sample_acquisition_get(data['sample'])

    print(result)

    assert result['sample'] == data['sample']


def test_sample_state():
    result = client.sample_state("Zeki_SIMVA_test_1uL.mzml")
    print(result)


def test_sample_result():
    result = client.sample_result("Zeki_SIMVA_test_1uL.mzml")
    print(result)


def test_sample_schedule():
    result = client.sample_state("Zeki_SIMVA_test_1uL.mzml")
    print(result)


def test_sample_exist():
    result = client.sample_state("Zeki_SIMVA_test_1uL.mzml")
    print(result)


def test_sample_metadata():
    result = client.sample_state("Zeki_SIMVA_test_1uL.mzml")
    print(result)


def test_experiment_samples():
    result = client.sample_state("Zeki_SIMVA_test_1uL.mzml")
    print(result)
