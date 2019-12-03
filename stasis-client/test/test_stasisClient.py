import os


def test_sample_acquisition_create(stasis_cli, sample):
    data = sample
    result = stasis_cli.sample_acquisition_create(data)
    assert 200 == result.status_code

    result = stasis_cli.sample_acquisition_get(data['sample'])
    assert data['sample'] == result['sample']


def test_acquisition_get(stasis_cli):
    result = stasis_cli.sample_acquisition_get(f'test_1')
    metadata = {'class': '123456',
                'organ': 'tissue',
                'species': 'rat'}
    assert metadata == result.get('metadata')


def test_sample_state(stasis_cli, sample):
    result = stasis_cli.sample_state_update(sample['sample'], 'entered')

    assert 200 == result.status_code
    assert 'entered' == stasis_cli.sample_state(sample['sample'])[0]['value']


def test_sample_result(stasis_cli):
    result = stasis_cli.sample_result('lgvty_cells_pilot_2_NEG_50K_BR_01.json')

    assert result is not None
    assert 'lgvty_cells_pilot_2_NEG_50K_BR_01' == result['sample']


def test_inexistent_result(stasis_cli):
    result = stasis_cli.sample_result('blah.blah')
    assert 'Error' in result
    assert 'blah.blah' == result.get('filename')


def test_persist_inexistent_file(stasis_cli):
    if os.path.exists('stfu/blah.blah'):
        os.remove('stfu/blah.blah')

    result = stasis_cli.sample_result('blah.blah', 'stfu')
    assert result['Error'] is not None
    assert os.path.exists('stfu/blah.blah') is False


def test_get_url(stasis_cli):
    assert "https://test-api.metabolomics.us/stasis" == stasis_cli.get_url()
