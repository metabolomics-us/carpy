import json
from time import sleep

from pytest import fail


def test_evaluate_empty_args(job_evaluator):
    result = job_evaluator.evaluate({})
    assert len(result) == 0


def test_evaluate_status(job_evaluator, test_job):
    result = job_evaluator.evaluate({'id': test_job['id'], 'status': True})
    assert len(result) == 1


def test_evaluate_exist(job_evaluator, test_job):
    result = job_evaluator.evaluate({'id': test_job['id'], 'exist': True})
    assert len(result) == 1
    assert result['exist'
           ] is True


def test_evaluate_not_exist(job_evaluator, test_job):
    result = job_evaluator.evaluate({'id': "fake_{}".format(test_job['id']), 'exist': True})
    assert len(result) == 1
    assert result['exist'] is False


def test_evaluate_process(job_evaluator, test_job):
    result = job_evaluator.evaluate({'id': test_job['id'], 'process': True})
    assert len(result) == 1


def test_evaluate_detail(job_evaluator, test_job, test_sample, test_sample_tracking_data):
    result = job_evaluator.evaluate({'id': test_job['id'], 'detail': True})
    assert len(result) == 1


def test_upload_and_process_and_monitor_and_download(job_evaluator, test_job, test_sample, tmp_path):
    print(tmp_path)

    test_job["method"] = "test | 6530 | test | positive",
    out = "{}/{}.json".format(str(tmp_path), test_job['id'])
    with open(out, 'w') as outfile:
        json.dump(test_job, outfile, indent=4)

    result = job_evaluator.evaluate({'id': test_job['id'], 'upload': out})['upload']

    assert result is True

    print("processing it now")

    job_evaluator.evaluate({'id': test_job['id'], 'process': True})

    print("monitoring")

    success = False
    for x in range(0, 100):
        result = job_evaluator.evaluate({'id': test_job['id'], 'monitor': True})
        if result['monitor']['job_state'] == 'failed':
            success = True
            break
        sleep(10)

    if success is False:
        fail()


def test_upload_and_process_and_monitor_and_failed(job_evaluator, test_job, test_sample, tmp_path):
    print(tmp_path)

    out = "{}/{}.json".format(str(tmp_path), test_job['id'])
    with open(out, 'w') as outfile:
        json.dump(test_job, outfile, indent=4)

    job_evaluator.evaluate({'id': test_job['id'], 'upload': out})

    print("processing it now")

    job_evaluator.evaluate({'id': test_job['id'], 'process': True})

    print("monitoring")

    success = False
    for x in range(0, 100):
        result = job_evaluator.evaluate({'id': test_job['id'], 'monitor': True})
        if result['monitor']['job_state'] == 'failed':
            success = True
            break
        sleep(10)

    if success is False:
        fail()
