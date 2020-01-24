import os

import pytest


@pytest.fixture()
def api_token():
    api_token = os.getenv('STASIS_API_TOKEN', '')
    assert api_token is not '', "please ensure you are setting the stasis api token in your env under STASIS_API_TOKEN!"

    print(api_token)
    return {'x-api-key': api_token.strip()}
