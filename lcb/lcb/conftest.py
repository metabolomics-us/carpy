import os

import pytest
from stasis_client.client import StasisClient

from lcb.evaluator import SampleEvaluator


@pytest.fixture
def stasis_cli():
    return StasisClient(os.getenv('STASIS_URL'), os.getenv('STASIS_API_TOKEN'))


@pytest.fixture
def sample_evaluator(stasis_cli):
    return SampleEvaluator(stasis=stasis_cli)


@pytest.fixture
def test_sample(stasis_cli):
    sample = {
        "acquisition": {
            "instrument": "6530test",
            "ionization": "positive",
            "method": "test"
        },
        "experiment": "teddy",
        "id": "lc-test-experiment",
        "metadata": {
            "organ": "test-organ",
            "species": "test-species"
        },
        "processing": {
            "method": "test | 6530test | test | positive"
        },
        "sample": "lc-test-sample",
        "time": 1563299315754
    }

    stasis_cli.sample_acquisition_create(data=sample)

    return sample
