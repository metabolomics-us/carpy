import sys
from abc import ABC
from typing import Optional

import requests as requests
from loguru import logger


class Similarity(ABC):
    """
    A client of the similarity4aws service
    """
    # initialize the loguru logger
    logger.add(sys.stdout, format="{time} {level} {message}", filter="Similarity", level="INFO", backtrace=False,
               diagnose=False)

    def __init__(self, url: Optional[str] = None):
        self._url = url if not url.endswith('/') else url[0:-1]

        if self._url is None:
            raise Exception("you need to provide a url in the env variable 'STASIS_API_URL'")

        self._header = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        self.http = requests.Session()

    def get_all_similarities(self, unknown: str, reference: str):
        result = self.http.get(f"{self._url}/all/{unknown}/{reference}", headers=self._header)

        if result.status_code == 200:
            return result.json()
        elif result.status_code in [400, 401]:
            logger.error(result.json()['error'])
            raise Exception(result.json()['error'])
        else:
            logger.error(result)
            raise Exception(result)

    def get_entropy_similarity(self, unknown: str, reference: str):
        return self._call_server(unknown, reference, 'entropy')

    def get_weighted_entropy_similarity(self, unknown: str, reference: str):
        return self._call_server(unknown, reference, 'weightedentropy')

    def get_total_similarity(self, unknown: str, reference: str):
        return self._call_server(unknown, reference, 'total')

    def get_cosine_similarity(self, unknown: str, reference: str):
        return self._call_server(unknown, reference, 'cosine')

    def get_reverse_similarity(self, unknown: str, reference: str):
        return self._call_server(unknown, reference, 'reverse')

    def get_presence_similarity(self, unknown: str, reference: str):
        return self._call_server(unknown, reference, 'presence')

    def get_nominal_cosine_similarity(self, unknown: str, reference: str):
        return self._call_server(unknown, reference, 'nominalcosine')

    def get_composite_similarity(self, unknown: str, reference: str):
        return self._call_server(unknown, reference, 'nominalcomposite')

    def _call_server(self, unknown: str, reference: str, algorithm: str):
        result = self.http.post(f"{self._url}/{algorithm}",
                                json={"a": unknown, "b": reference}, headers=self._header)

        if result.status_code == 200:
            return result.json()
        elif result.status_code in [400, 401]:
            logger.error(result.json()['error'])
            raise Exception(result.json()['error'])
        else:
            logger.error(result)
            raise Exception(result)
