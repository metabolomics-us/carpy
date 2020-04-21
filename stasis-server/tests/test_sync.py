from stasis.bucket.triggers import bucket_zip
from stasis.jobs.schedule import schedule_job
from stasis.service.Status import EXPORTED, PROCESSING, FAILED, AGGREGATING_SCHEDULING, SCHEDULED, AGGREGATED, \
    AGGREGATING_SCHEDULED, AGGREGATED_AND_UPLOADED
from stasis.tables import save_sample_state, get_job_state


def test_calculate_job_state_with_zip_upload(requireMocking, mocked_10_sample_job):
    # set 1 sample state to exported
    save_sample_state(sample="abc_0", state=EXPORTED)
    # this should update the job state accordingly to processing
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
    # this should set the job state to aggregation scheduling now
    state = get_job_state("12345")
    assert state == AGGREGATING_SCHEDULED


def test_calculate_job_state_2(requireMocking, mocked_10_sample_job):
    result = schedule_job({'pathParameters': {
        "job": "12345"
    }}, {})
    state = get_job_state("12345")
    assert state == SCHEDULED

    # set 1 sample state to failed
    save_sample_state(sample="abc_0", state=FAILED)
    # this should update the job state accordingly to processing
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
    # this should set the job state to aggregation scheduling now
    state = get_job_state("12345")
    assert state == AGGREGATING_SCHEDULED
