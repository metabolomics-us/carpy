def test_evaluate_no_args(sample_evaluator):
    sample_evaluator.evaluate({})
    pass


def test_evaluate_sample_job_and_status(sample_evaluator, test_sample):
    sample_evaluator.evaluate({'id': test_sample['sample'], 'status': True})
    pass


def test_evaluate_sample_job_and_process(sample_evaluator, test_sample):
    sample_evaluator.evaluate({'id': test_sample['sample'], 'process': True, 'profile': 'lcms', 'env': 'test'})
    pass


def test_evaluate_sample_job_and_download(sample_evaluator, test_sample):
    sample_evaluator.evaluate({'id': test_sample['sample'], 'download': True})
    pass


def test_evaluate_sample_job_and_exist(sample_evaluator, test_sample):
    sample_evaluator.evaluate({'id': test_sample['sample'], 'exist': True})
    pass


def test_evaluate_sample_job_and_info(sample_evaluator, test_sample):
    sample_evaluator.evaluate({'id': test_sample['sample'], 'info': True})
    pass
