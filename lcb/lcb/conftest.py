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
