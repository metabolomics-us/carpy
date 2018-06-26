import time

import pytest
import simplejson as json

from stasis.acquisition import create as acq_create
from stasis.tracking import create


def test_create_success(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps({'sample': 'myTest', 'status': 'entered'})

    response = create.create({'body': jsonString}, {})
    assert response['ResponseMetadata']['HTTPStatusCode'], 200

    assert 'entered' == response['Attributes']['status'][0]['value']
    assert timestamp <= response['Attributes']['status'][0]['time']


def test_create_with_fileHandle(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps({'sample': 'myTest', 'status': 'entered', 'fileHandle': 'myTest.d'})

    response = create.create({'body': jsonString}, {})

    assert response['ResponseMetadata']['HTTPStatusCode'], 200

    data = response['Attributes']

    assert 'entered' == data['status'][0]['value']
    assert timestamp <= data['status'][0]['time']
    assert 'myTest.d' == data['status'][0]['fileHandle']


def test_create_fail_invalid_status(requireMocking):
    with pytest.raises(Exception):
        create.create({'body': json.dumps({'sample': 'test', 'status': 'not a valid status'})}, {})


def test_create_success_with_substatus(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps({'sample': 'myTest', 'status': 'corrected'})

    response = create.create({'body': jsonString}, {})

    assert response['ResponseMetadata']['HTTPStatusCode'], 200

    data = response['Attributes']
    assert 'corrected' == data['status'][0]['value']
    assert timestamp <= data['status'][0]['time']


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

    print(results)


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
    assert 200 == response['ResponseMetadata']['HTTPStatusCode']
    time.sleep(2)

    track = {
        'sample': 'test_experiment',
        'status': 'entered'
    }
    print('creating tracking data')
    response = create.create({'body': json.dumps(track)}, {})

    assert 200 == response['statusCode']
    assert '1' == json.loads(response['body'])['experiment']
