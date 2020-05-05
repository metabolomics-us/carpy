from pytest import fail

from stasis.bucket.triggers import bucket_zip
from stasis.jobs.schedule import schedule_job
from stasis.jobs.sync import do_sync, sync_job
from stasis.service.Status import EXPORTED, PROCESSING, FAILED, AGGREGATING_SCHEDULING, SCHEDULED, AGGREGATED, \
    AGGREGATING_SCHEDULED, AGGREGATED_AND_UPLOADED
from stasis.tables import save_sample_state, get_job_state, get_job_config
from tests.stasis.jobs.test_schedule import watch_job_schedule_queue


def test_calculate_job_state_with_zip_upload(requireMocking, mocked_10_sample_job):
    # set 1 sample state to exported
    save_sample_state(sample="abc_0", state=EXPORTED)
    # this should update the job state accordingly to processing
    sync_job(get_job_config("12345"))
    state = get_job_state("12345")
    assert state == PROCESSING
    # set sample state to failed
    save_sample_state(sample="abc_1", state=FAILED)
    sync_job(get_job_config("12345"))
    # this should keep the job state in state processing
    state = get_job_state("12345")
    assert state == PROCESSING

    # set all other samples to exported

    save_sample_state(sample="abc_2", state=EXPORTED)
    save_sample_state(sample="abc_3", state=EXPORTED)
    save_sample_state(sample="abc_4", state=EXPORTED)
    save_sample_state(sample="abc_5", state=EXPORTED)
    save_sample_state(sample="abc_6", state=EXPORTED)
    save_sample_state(sample="abc_7", state=EXPORTED)
    save_sample_state(sample="abc_8", state=EXPORTED)
    save_sample_state(sample="abc_9", state=EXPORTED)
    sync_job(get_job_config("12345"))
    # this should set the job state to aggregation scheduling now
    state = get_job_state("12345")
    assert state == AGGREGATING_SCHEDULED

    # trigger an upload to the zip bucket
    bucket_zip(
        {
            'Records': [{
                's3': {
                    'object': {
                        'key': '12345.zip'
                    }
                }
            }
            ]
        }

        , {})

    # job should now be aggregated
    state = get_job_state("12345")
    assert state == AGGREGATED_AND_UPLOADED


def test_calculate_job_state(requireMocking, mocked_10_sample_job):
    # set 1 sample state to exported
    save_sample_state(sample="abc_0", state=EXPORTED)
    # this should update the job state accordingly to processing
    sync_job(get_job_config("12345"))
    state = get_job_state("12345")
    assert state == PROCESSING
    # set sample state to failed
    save_sample_state(sample="abc_1", state=FAILED)
    # this should keep the job state in state processing
    state = get_job_state("12345")
    assert state == PROCESSING

    # set all other samples to exported

    save_sample_state(sample="abc_2", state=EXPORTED)
    save_sample_state(sample="abc_3", state=EXPORTED)
    save_sample_state(sample="abc_4", state=EXPORTED)
    save_sample_state(sample="abc_5", state=EXPORTED)
    save_sample_state(sample="abc_6", state=EXPORTED)
    save_sample_state(sample="abc_7", state=EXPORTED)
    save_sample_state(sample="abc_8", state=EXPORTED)
    save_sample_state(sample="abc_9", state=EXPORTED)
    sync_job(get_job_config("12345"))
    # this should set the job state to aggregation scheduling now
    state = get_job_state("12345")
    assert state == AGGREGATING_SCHEDULED


def test_calculate_job_state_2(requireMocking, mocked_10_sample_job):
    result = schedule_job({'pathParameters': {
        "job": "12345"
    }}, {})

    watch_job_schedule_queue()
    state = get_job_state("12345")
    assert state == SCHEDULED

    # set 1 sample state to failed
    save_sample_state(sample="abc_0", state=FAILED)
    sync_job(get_job_config("12345"))
    # this should update the job state accordingly to processing
    state = get_job_state("12345")

    assert state == PROCESSING
    # set sample state to failed
    save_sample_state(sample="abc_1", state=FAILED)
    # this should keep the job state in state processing
    sync_job(get_job_config("12345"))
    state = get_job_state("12345")
    assert state == PROCESSING

    # set all other samples to exported

    save_sample_state(sample="abc_2", state=EXPORTED)
    save_sample_state(sample="abc_3", state=EXPORTED)
    save_sample_state(sample="abc_4", state=EXPORTED)
    save_sample_state(sample="abc_5", state=EXPORTED)
    save_sample_state(sample="abc_6", state=EXPORTED)
    save_sample_state(sample="abc_7", state=EXPORTED)
    save_sample_state(sample="abc_8", state=EXPORTED)
    save_sample_state(sample="abc_9", state=EXPORTED)
    sync_job(get_job_config("12345"))
    # this should set the job state to aggregation scheduling now
    state = get_job_state("12345")
    assert state == AGGREGATING_SCHEDULED


def test_do_sync(requireMocking):
    event = {'Records': [{'messageId': '7cecc6ca-7067-4aaf-a990-6d1dd42b68be',
                  'receiptHandle': 'AQEBAEMtMa9/K6xyHQGtWpsKEsYekPYLQVVGmUxmMAxxY5e8S96EeTF8uo3EvLwIu7d2q3v953JL28y7Evueb7QrvnPCY47XXauIkT9eQ2XX8XjDIGe7/8UgOWy3HsU/QamXKACB7Bhc2YtEJzjpzX79XvBs40MYh1sDHZ/QlNUx628b124tJnNEzmR3v3iJ10YiDe0TpRwpqxTZbi+lQhHu+x/nwNJlA3jxZXBqjQTpbsYCW0WkTS8ejwQ68IOSBRCNwv8/YArJsvU1+sQPz7Bjvlo9myD1P6GO9dMJnQU8hCDt3faaN9GyrnL1BCeylviqNhNxCk4fsfYVtYyE3H1qbJe+7iasVXfFPIbY7Wrzue6gi655L3PhPnx5apIGG/zkExN0pqrZIzkiMzpp+8Dd8g==',
                  'body': '{"default": "{\\"job\\": \\"test_job_1587593202.6542692\\"}"}',
                  'attributes': {'ApproximateReceiveCount': '17', 'SentTimestamp': '1587746738625',
                                 'SenderId': 'AROA2HEI3O7NIZM3ZYGKH:stasis-test-trackingCreate',
                                 'ApproximateFirstReceiveTimestamp': '1587746738625'}, 'messageAttributes': {},
                  'md5OfBody': 'd42ce3a80d7c953c933e8022c5d29a79', 'eventSource': 'aws:sqs',
                  'eventSourceARN': 'arn:aws:sqs:us-west-2:702514165722:StasisSyncQueue-test',
                  'awsRegion': 'us-west-2'}]}

    do_sync(event,{})