import os

import pytest


@pytest.fixture()
def api_token():
    api_token ='9MjbJRbAtj8spCJJVTPbP3YWc4wjlW0c7AP47Pmi'
    assert api_token is not '', "please ensure you are setting the stasis api token in your env under STASIS_API_TOKEN!"

    print(api_token)
    return {'x-api-key': api_token.strip()}
