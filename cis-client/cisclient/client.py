import os
from typing import Optional, List

import requests
from requests.adapters import HTTPAdapter, Retry


class CISClient:
    """
    a simple client to interact with the cis system in a safe and secure manner.
    """

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        """
        the client requires an url where to connect against
        and the related token.

        Args:
            url:
            token:
        """

        self._url = url
        self._token = token

        if self._token is None:
            # utilize env
            self._token = os.getenv('CIS_API_TOKEN', os.getenv('PROD_CIS_API_TOKEN'))
        if self._url is None:
            self._url = os.getenv('CIS_API_URL', 'https://api.metabolomics.us/cis')

        if self._token is None:
            raise Exception("you need to to provide a cis api token in the env variable 'CIS_API_TOKEN'")

        if self._url is None:
            raise Exception("you need to provide a url in the env variable 'CIS_API_URL'")

        self._header = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': f'{self._token}'
        }

        retry_strategy = Retry(
            total=500,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http = requests.Session()

    def get_libraries(self) -> List[str]:
        result: requests.Response = self.http.get(f"{self._url}/libraries", headers=self._header)
        if result.status_code == 200:
            return result.json()
        else:
            raise Exception(result)

    def exists_library(self, library: str) -> bool:
        result = self.http.head(f"{self._url}/libraries/{library}", headers=self._header)

        if result.status_code == 200:
            return True
        elif result.status_code == 404:
            return False
        else:
            raise Exception(result)

    def get_compounds(self, library: str) -> List[dict]:
        limit = 10
        offset = 0
        result = self.http.get(f"{self._url}/compounds/{library}/{limit}/{offset}", headers=self._header)

        if result.status_code == 200:
            return result.json()
        else:
            raise Exception(result)

    def exists_compound(self, library: str, splash: str) -> bool:
        result = self.http.head(f"{self._url}/compound/{library}/{splash}", headers=self._header)

        if result.status_code == 200:
            return True
        elif result.status_code == 404:
            return False
        else:
            raise Exception(result)

    def get_compound(self, library: str, splash: str) -> dict:
        result = self.http.get(f"{self._url}/compound/{library}/{splash}", headers=self._header)

        if result.status_code == 200:
            return result.json()[0]
        else:
            raise Exception(result)