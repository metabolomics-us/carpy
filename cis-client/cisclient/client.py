import os
import sys
from typing import Optional, List

import requests
from loguru import logger
from requests.adapters import HTTPAdapter, Retry

import pprint

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="cisclient", level="INFO", backtrace=True,
           diagnose=True)


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

    @logger.catch
    def get_libraries(self) -> List[str]:
        result: requests.Response = self.http.get(f"{self._url}/libraries", headers=self._header)
        if result.status_code == 200:
            return result.json()
        else:
            raise Exception(result)

    @logger.catch
    def size_library(self, library) -> List[str]:
        result: requests.Response = self.http.get(f"{self._url}/libraries/{library}", headers=self._header)
        if result.status_code == 200:
            return result.json()
        else:
            raise Exception(result)

    @logger.catch
    def exists_library(self, library: str) -> bool:
        result = self.http.head(f"{self._url}/libraries/{library}", headers=self._header)

        if result.status_code == 200:
            return True
        elif result.status_code == 404:
            return False
        else:
            raise Exception(result)

    @logger.catch
    def get_compounds_by_type(self, library: str, target_type: str, offset: int = 0, autopage: bool = True) -> List[
        dict]:
        limit = 10
        result = self.http.get(f"{self._url}/oldcompounds/{library}/{limit}/{offset}/{target_type}",
                               headers=self._header)

        if result.status_code == 200:
            result: List = result.json()

            if autopage:
                data = result

                while len(data) > 0:
                    # avoid recursive calls
                    offset = offset + limit
                    data = self.get_compounds_by_type(library=library, offset=offset, autopage=False,
                                                      target_type=target_type)

                    for x in data:
                        result.append(x)

            return result

        elif result.status_code == 404:
            return []
        else:
            raise Exception(result)

    @logger.catch
    def get_compounds(self, library: str, offset: int = 0, autopage: bool = True) -> List[dict]:
        limit = 10
        result = self.http.get(f"{self._url}/oldcompounds/{library}/{limit}/{offset}", headers=self._header)

        if result.status_code == 200:
            result: List = result.json()

            if autopage:
                data = result

                while len(data) > 0:
                    # avoid recursive calls
                    offset = offset + limit
                    data = self.get_compounds(library=library, offset=offset, autopage=False)

                    for x in data:
                        result.append(x)

            return result

        elif result.status_code == 404:
            return []
        else:
            raise Exception(result)

    @logger.catch
    def get_members(self, library: str, splash: str, offset: int = 0, autopage: bool = True) -> List[dict]:
        limit = 10
        result = self.http.get(f"{self._url}/compound/members/{library}/{splash}/{limit}/{offset}",
                               headers=self._header)

        if result.status_code == 200:
            result: List = result.json()
            if autopage:
                for x in self.get_members(library=library, splash=splash, offset=offset + limit):
                    result.append(x)
            return result


        elif result.status_code == 404:
            return []
        else:
            raise Exception(result)

    @logger.catch
    def has_members(self, splash: str, library: str):
        """
        returns all members of a consensus spectra
        :param splash:
        :param library:
        :return:
        """
        result = self.http.head(f"{self._url}/compound/members/{library}/{splash}", headers=self._header)

        if result.status_code == 200:
            return True
        elif result.status_code == 404:
            return False
        else:
            raise Exception(result)

    @logger.catch
    def exists_compound(self, library: str, splash: str) -> bool:
        result = self.http.head(f"{self._url}/compound/{library}/{splash}", headers=self._header)

        if result.status_code == 200:
            return True
        elif result.status_code == 404:
            return False
        else:
            raise Exception(result)

    @logger.catch
    def compound_add_adduct(self, library: str, splash: str, name: str, identifiedBy: str, comment: str):
        result = self.http.post(f"{self._url}/compound/adduct/{library}/{splash}/{identifiedBy}/{name}",
                                headers=self._header, data=comment)

        if result.status_code != 200:
            raise Exception(result)

    @logger.catch
    def compound_remove_adduct(self, library: str, splash: str, name: str, identifiedBy: str) -> bool:
        result = self.http.delete(f"{self._url}/compound/adduct/{library}/{splash}/{identifiedBy}/{name}",
                                  headers=self._header)

        return result.status_code == 200

    @logger.catch
    def compound_delete_adduct(self, library: str, splash: str, name: str, identifiedBy: str):
        result = self.http.delete(f"{self._url}/compound/adduct/{library}/{splash}/{identifiedBy}/{name}",
                                  headers=self._header)

        if result.status_code != 200:
            raise Exception(result)

    @logger.catch
    def name_compound(self, library: str, splash: str, name: str, identifiedBy: str, comment: str):
        result = self.http.post(f"{self._url}/compound/identify/{library}/{splash}/{identifiedBy}/{name}",
                                headers=self._header, data=comment)

        if result.status_code != 200:
            raise Exception(result)

    @logger.catch
    def delete_name_compound(self, library: str, splash: str, name: str, identifiedBy: str):
        result = self.http.delete(f"{self._url}/compound/identify/{library}/{splash}/{identifiedBy}/{name}",
                                  headers=self._header)

        if result.status_code != 200:
            raise Exception(result)

    @logger.catch
    def set_compound_primary_name(self, library: str, splash: str, name: str) -> dict:
        result = self.http.put(f"{self._url}/compound/{library}/{splash}/{name}", headers=self._header)

        if result.status_code == 200:
            return self.get_compound(library, splash)
        else:
            raise Exception(result)

    @logger.catch
    def get_compound(self, library: str, splash: str) -> dict:
        result = self.http.get(f"{self._url}/compound/{library}/{splash}", headers=self._header)

        if result.status_code == 200:
            return result.json()[0]
        else:
            raise Exception(result)

    @logger.catch
    def get_profiles(self, object_type: str, object_id: str):
        if object_type not in ['target', 'sample']:
            raise Exception('object_type should be "target" or "sample"')

        result = self.http.get(f'{self._url}/profiles/{object_type}/{object_id}', headers=self._header)

        if result.status_code == 200:
            return result.json()
        else:
            raise Exception(result)

    @logger.catch
    def get_configs(self, object_type: str, object_id: str):
        if object_type not in ['target', 'sample']:
            raise Exception('object_type should be "target" or "sample"')

        result = self.http.get(f'{self._url}/configurations/{object_type}/{object_id}', headers=self._header)

        if result.status_code == 200:
            return result.json()
        else:
            raise Exception(result)

    @logger.catch
    def get_sorted_compounds(self, library: str, tgt_type: str = None, limit: int = 10, offset: int = 0,
                             order_by: str = id, direction: str = 'asc'):

        url_path = f'{self._url}/compounds/{library}'

        if tgt_type is not None and tgt_type.strip() != "":
            url_path = url_path + f'/{tgt_type}'

        url_query_string = f'limit={limit}&offset={offset}&order_by={order_by}&direction={direction}'

        result = self.http.get(f'{url_path}?{url_query_string}', headers=self._header)

        if result.status_code == 200:
            return result.json()
        else:
            raise Exception(result)

    
    @logger.catch
    def get_annotations_given_splash(self, splash: str, limit: int = 10, offset: int = 0, autopage: bool = True):
        """
        Opted to make limit a positional argument. dont think it should be hardcoded.
        We do not accept a null value for limit and offset (althought the server does not complain per postmates get)
        instead we suppose the defaults.
        :param splash: hashed identifier that describes the bin of spectra for which you are interested
        :param limit: the number of results returned with each iteration of calls
        :param offset: the position at which you want results to start. incremented over iterations
        :return: returns a .json format dictionary containing all annotations corresponding to the specified bin
        """
        url_path = f'{self._url}/annotations/{splash}'

        url_query_string = f'limit={limit}&offset={offset}'

        result = self.http.get(f'{url_path}?{url_query_string}', headers=self._header)

        if result.status_code == 200:
            result: dict = result.json()

            if autopage:
                #data is entire dictionary
                data=result

                while len(data['annotations']) > 0:
                    offset=limit+offset
                    data=self.get_annotations_given_splash(splash=splash,limit=limit,offset=offset,autopage=False)
                    for x in data['annotations']:
                        result['annotations'].append(x)
            
            return result
        elif result.status_code == 404:
            return {'annotations':[]}
        else:
            raise Exception(result)


    @logger.catch
    def get_spectrum_status(self, target_id: int, limit: int = 10, offset: int = 0):
        """
        Get the 'clean or dirty' status for a target
        :param target_id: Target id (not splash)
        :param limit: number of results to be returned (used on paging)
        :param offset: start collecting results from this row number (used on paging)
        :return:
        """
        url_path = f'{self._url}/spectrum/{target_id}'

        url_query_string = f'limit={limit}&offset={offset}'

        result = self.http.get(f'{url_path}?{url_query_string}', headers=self._header)

        if result.status_code == 200:
            return result.json()
        else:
            raise Exception(result)
