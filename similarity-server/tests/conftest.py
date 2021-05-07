import os

import moto as moto
import pytest


@pytest.fixture
def require_mocking():
    """
    method which should be called before all other methods in tests. It basically configures our
    mocking context for stasis
    """

    lamb = moto.mock_lambda()
    lamb.start()

    os.environ["current_stage"] = "test"

    yield
    lamb.stop()

    pass


@pytest.fixture
def spectrum_pair():
    return {
        "unknown": "10:100 20:150 25:10",
        "reference": "10:100 25:150"
    }
