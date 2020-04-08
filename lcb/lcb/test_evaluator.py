def test_evaluate_empty_args(sample_evaluator):
    result = sample_evaluator.evaluate({})
    pass
    assert len(result) == 0


def test_evaluate_sample_and_status(sample_evaluator, test_sample):
    result = sample_evaluator.evaluate({'id': test_sample['sample'], 'status': True})
    pass
    assert len(result) == 1


def test_evaluate_sample_and_process(sample_evaluator, test_sample):
    result = sample_evaluator.evaluate({'id': test_sample['sample'], 'process': True, 'profile': 'lcms', 'env': 'test'})
    pass
    assert len(result) == 1


def test_evaluate_sample_and_download(sample_evaluator, test_sample, test_sample_result):
    result = sample_evaluator.evaluate({'id': test_sample['sample'], 'retrieve': True})
    assert len(result) == 1


def test_evaluate_sample_and_exist(sample_evaluator, test_sample):
    result = sample_evaluator.evaluate({'id': test_sample['sample'], 'exist': True})
    pass
    assert len(result) == 1


def test_evaluate_sample_and_info(sample_evaluator, test_sample):
    result = sample_evaluator.evaluate({'id': test_sample['sample'], 'detail': True})
    pass
    assert len(result) == 1
