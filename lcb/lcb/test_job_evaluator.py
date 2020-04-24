import json

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
           ] == True


def test_evaluate_not_exist(job_evaluator, test_job):
    result = job_evaluator.evaluate({'id': "fake_{}".format(test_job['id']), 'exist': True})
    assert len(result) == 1
    assert result['exist'] == False


def test_evaluate_process(job_evaluator, test_job):
    result = job_evaluator.evaluate({'id': test_job['id'], 'process': True})
    assert len(result) == 1


def test_evaluate_detail(job_evaluator, test_job, test_sample, test_sample_tracking_data):
    result = job_evaluator.evaluate({'id': test_job['id'], 'detail': True})
    assert len(result) == 1


def test_upload(job_evaluator, test_job, test_sample, tmp_path):
    print(tmp_path)

    out = "{}/{}.json".format(str(tmp_path), test_job['id'])
    with open(out, 'w') as outfile:
        json.dump(test_job, outfile, indent=4)

    fail()
