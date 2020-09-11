import time

import pytest
import simplejson as json

from stasis.acquisition import create as acq_create
from stasis.service.Status import ENTERED, ACQUIRED, CONVERTED, SCHEDULING, PROCESSING, DECONVOLUTED, CORRECTED, \
    ANNOTATED, QUANTIFIED, REPLACED, EXPORTED, SCHEDULED
from stasis.tables import _remove_reinjection
from stasis.tracking import create


@pytest.mark.parametrize('state',
                         [ENTERED, ACQUIRED, CONVERTED, SCHEDULING, SCHEDULED, PROCESSING, DECONVOLUTED, CORRECTED,
                          ANNOTATED,
                          QUANTIFIED, REPLACED, EXPORTED])
def test_create_success(requireMocking, state):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps({'sample': 'myTest', 'status': state})

    response = create.create({'body': jsonString}, {})
    assert 'isBase64Encoded' in response
    assert response['statusCode'] == 200

    assert state == json.loads(response['body'])['status'][0]['value']
    assert timestamp <= json.loads(response['body'])['status'][0]['time']


def test_create_with_fileHandle(requireMocking):
    timestamp = int(time.time() * 1000)

    data = json.dumps({'sample': 'myTest', 'status': 'entered', 'fileHandle': 'myTest.d'})

    response = create.create({'body': data}, {})
    assert 'isBase64Encoded' in response
    assert response['statusCode'] == 200

    assert 'entered' == json.loads(response['body'])['status'][0]['value']
    assert timestamp <= json.loads(response['body'])['status'][0]['time']
    assert 'myTest.d' == json.loads(response['body'])['status'][0]['fileHandle']


def test_create_fail_invalid_status(requireMocking):
    with pytest.raises(Exception):
        create.create({'body': json.dumps({'sample': 'test', 'status': 'not a valid status'})}, {})


def test_create_success_with_substatus(requireMocking):
    timestamp = int(time.time() * 1000)

    data = json.dumps({'sample': 'myTest', 'status': 'corrected'})

    response = create.create({'body': data}, {})
    assert 'isBase64Encoded' in response
    assert response['statusCode'] == 200

    assert 'corrected' == json.loads(response['body'])['status'][0]['value']
    assert timestamp <= json.loads(response['body'])['status'][0]['time']


def test_status_merging(requireMocking):
    data = [{'sample': 'processed-sample', 'status': 'entered'},
            {'sample': 'processed-sample', 'status': 'acquired'},
            {'sample': 'processed-sample', 'status': 'converted'},
            {'sample': 'processed-sample', 'status': 'processing'},
            {'sample': 'processed-sample', 'status': 'deconvoluted'},
            {'sample': 'processed-sample', 'status': 'corrected'},
            {'sample': 'processed-sample', 'status': 'annotated'},
            {'sample': 'processed-sample', 'status': 'quantified'},
            {'sample': 'processed-sample', 'status': 'replaced'},
            {'sample': 'processed-sample', 'status': 'exported'}]

    results = [create.create({'body': json.dumps(x)}, {}) for x in data]

    print("RESULTS: %s" % json.dumps(results, indent=2))


# skipped due to all experiments set to unknown for now
@pytest.mark.skip
def test_create_with_experiment(requireMocking):
    data = {
        'sample': 'test_experiment',
        'experiment': '1',
        'acquisition': {'instrument': 'test inst', 'name': 'method blah',
                        'ionisation': 'positive',  # psotivie || negative
                        'method': 'gcms'  # gcms || lcms
                        },
        'processing': {'method': 'gcms'},
        'metadata': {'class': '12345', 'species': 'alien', 'organ': 'honker'},
        'userdata': {'label': 'filexxx', 'comment': ''},
    }

    print('bootstraping acquisition data')
    response = acq_create.create({'body': json.dumps(data)}, {})
    assert 'isBase64Encoded' in response
    assert 200 == response['statusCode']
    time.sleep(1)

    track = {
        'sample': 'test_experiment',
        'status': 'entered'
    }
    response = create.create({'body': json.dumps(track)}, {})
    assert 'isBase64Encoded' in response
    assert 200 == response['statusCode']
    assert '1' == json.loads(response['body'])['experiment']
    assert 'test_experiment' == json.loads(response['body'])['sample']


def test_fetching_reinjection(requireMocking):
    data = ['reinjected_2', 'reinjected_BU', 'reinjected_3']

    cleaned = [_remove_reinjection(x) for x in data]

    assert all([x == 'reinjected' for x in cleaned])


def test_create_reinjection(requireMocking):
    data = {
        'sample': 'test_reinjected',
        'experiment': 'myReinjectionTest',
        'acquisition': {'instrument': 'test inst', 'name': 'method blah',
                        'ionisation': 'positive',  # psotivie || negative
                        'method': 'gcms'  # gcms || lcms
                        },
        'processing': {'method': 'gcms'},
        'metadata': {'class': '12345', 'species': 'alien', 'organ': 'honker'},
        'userdata': {'label': 'filexxx', 'comment': ''},
    }

    print('bootstraping acquisition data')
    response = acq_create.create({'body': json.dumps(data)}, {})
    assert 'isBase64Encoded' in response
    assert 200 == response['statusCode']
    time.sleep(1)

    tracking = [{'sample': 'test_reinjected_2', 'status': 'acquired', 'fileHandle': 'test_reinjected_2.mzml'},
                {'sample': 'test_reinjected_BU', 'status': 'acquired', 'fileHandle': 'test_reinjected_BU.mzml'}]

    responses = [create.create({'body': json.dumps(x)}, {}) for x in tracking]

    print([json.loads(s['body']) for s in responses])

