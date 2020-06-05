import json

import pytest
import yaml
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


def test_upload_as_json(job_evaluator, test_job_definition, test_sample, tmp_path):
    test_job = test_job_definition
    test_job["method"] = "teddy | 6530 | test | positive"
    test_job["id"] = "my_test_job_for_lcb_success"

    out = "{}/{}.json".format(str(tmp_path), test_job['id'])
    with open(out, 'w') as outfile:
        json.dump(test_job, outfile, indent=4)

    result = job_evaluator.evaluate({'id': test_job['id'], 'upload': out})['upload']

    assert result is True


def test_upload_as_yaml(job_evaluator, test_job_definition, test_sample, tmp_path):
    test_job = test_job_definition
    test_job["method"] = "teddy | 6530 | test | positive"
    test_job["id"] = "my_test_job_for_lcb_success"

    out = "{}/{}.yaml".format(str(tmp_path), test_job['id'])
    with open(out, 'w') as outfile:
        yaml.dump(test_job, outfile, indent=4)

    result = job_evaluator.evaluate({'id': test_job['id'], 'upload': out})['upload']

    assert result is True


def test_upload_as_yml(job_evaluator, test_job_definition, test_sample, tmp_path):
    test_job = test_job_definition
    test_job["method"] = "teddy | 6530 | test | positive"
    test_job["id"] = "my_test_job_for_lcb_success"

    out = "{}/{}.yml".format(str(tmp_path), test_job['id'])
    with open(out, 'w') as outfile:
        yaml.dump(test_job, outfile, indent=4)

    result = job_evaluator.evaluate({'id': test_job['id'], 'upload': out})['upload']

    assert result is True


def test_upload_as_not_supported_extension(job_evaluator, test_job_definition, test_sample, tmp_path):
    test_job = test_job_definition
    test_job["method"] = "teddy | 6530 | test | positive"
    test_job["id"] = "my_test_job_for_lcb_success"

    out = "{}/{}.fail".format(str(tmp_path), test_job['id'])
    with open(out, 'w') as outfile:
        yaml.dump(test_job, outfile, indent=4)

    try:
        result = job_evaluator.evaluate({'id': test_job['id'], 'upload': out})['upload']
        fail()
    except:
        pass


@pytest.mark.parametrize("rerun", [1, 2, 3])
def test_upload_and_process_and_monitor_and_download(job_evaluator, test_job_definition, test_sample, tmp_path, rerun):
    test_job = test_job_definition
    test_job["method"] = "teddy | 6530 | test | positive"
    test_job["id"] = "my_test_job_for_lcb_success"

    out = "{}/{}.json".format(str(tmp_path), test_job['id'])
    with open(out, 'w') as outfile:
        json.dump(test_job, outfile, indent=4)

    result = job_evaluator.evaluate({'id': test_job['id'], 'upload': out})['upload']

    assert result is True

    print("processing it now")

    job_evaluator.evaluate({'id': test_job['id'], 'process': True})

    print("monitoring")

    result = job_evaluator.evaluate(
        {'id': test_job['id'],  'wait_for': ['aggregated_and_uploaded'], 'wait_attempts': 100,
         'wait_time': 10})['wait_for']

    if result is False:
        fail()

    result = job_evaluator.evaluate({'id': test_job_definition['id'], 'retrieve': str(tmp_path.absolute())})[
        'retrieve']
    if result is False:
        fail("were not able to download {}".format(test_job_definition['id']))


def test_upload_and_process_and_monitor_and_failed(job_evaluator, test_job_definition, test_sample, tmp_path):
    test_job = test_job_definition
    test_job["id"] = "my_test_job_for_lcb_failed"
    test_job["method"] = "teddy | 6530noexist | test | positive"

    out = "{}/{}.json".format(str(tmp_path), test_job['id'])
    with open(out, 'w') as outfile:
        json.dump(test_job, outfile, indent=4)

    job_evaluator.evaluate({'id': test_job['id'], 'upload': out})

    print("processing it now")

    job_evaluator.evaluate({'id': test_job['id'], 'process': True})

    print("monitoring")

    result = job_evaluator.evaluate(
        {'id': test_job['id'],  'wait_for': ['failed'], 'wait_attempts': 100,
         'wait_time': 10})[
        'wait_for']
    if result is False:
        fail()
