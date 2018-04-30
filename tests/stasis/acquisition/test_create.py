import json
import time

import pytest

from stasis.acquisition import create
from stasis.util.minix_parser import parse_minix_xml


def test_create_success_gctof(requireMocking):
    data = parse_minix_xml("http://minix.fiehnlab.ucdavis.edu/rest/export/382171")

    timestamp = int(time.time() * 1000)

    for x in data:
        jsonString = json.dumps(x)

        response = create.create({'body': jsonString}, {})

        assert response["statusCode"], 200
        assert json.loads(response["body"])["acquisition"]['instrument'] == "Leco GC-Tof"
        assert json.loads(response["body"])["acquisition"]['name'] == "GCTOF"
        assert json.loads(response["body"])["acquisition"]['ionisation'] == "positive"
        assert json.loads(response["body"])["acquisition"]['method'] == "gcms"
        assert json.loads(response["body"])["metadata"]['species'] == "rat"
        assert json.loads(response["body"])["metadata"]['organ'] == "tissue"
