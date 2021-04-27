import sys

import pytest
from loguru import logger

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="conftest", level="INFO", backtrace=True,
           diagnose=True)


@pytest.fixture
def splash_pair():
    return {"unk": "splash10-001i-0900000000-3d6dc85dd803cceed54e",
            "ref": "splash10-001i-1900000000-90c2c61af7ad1b4a6f2e"}


@pytest.fixture
def spectrum_pair():
    return {
        "unk": "80.765000:1760.65 81.070000:6983.60 95.085000:19192.86 105.065000:1994.32 105.070000:2730.00 107.950000:1894.58 112.850000:2084.40 123.055000:4453.16 123.080000:401874.31",
        "ref": "80.765000:1760.65 81.070000:6571.81 95.085000:17581.47 105.065000:1994.32 107.950000:1894.58 110.645000:1992.41 123.080000:401593.19"}
