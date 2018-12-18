import os

import pytest


@pytest.fixture()
def api_token():
    api_token = os.getenv('STASIS_API_TOKEN', '')
    if api_token is '':
        api_token = open('../../../test.env', 'r').readline()

    return {'x-api-key': api_token}
