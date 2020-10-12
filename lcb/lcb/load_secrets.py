import os

from boto3 import Session
from get_docker_secret import get_docker_secret


class Secrets:
    """
    helper class to provides us with a dict of all the system wide secrets, depending if it runs inside of docker
    or inside the os
    """

    def load(self) -> dict:
        session = Session()
        credentials = session.get_credentials()
        current_credentials = credentials.get_frozen_credentials()
        return {

            'CIS_TOKEN': get_docker_secret('CIS_TOKEN', default=os.getenv('CIS_TOKEN',os.getenv('CIS_API_TOKEN'))),
            'CIS_URL': get_docker_secret('CIS_URL', default=os.getenv('CIS_URL',os.getenv('CIS_API_URL'))),
            'STASIS_TOKEN': get_docker_secret('STASIS_TOKEN', default=os.getenv('STASIS_TOKEN',os.getenv('STASIS_API_TOKEN'))),
            'STASIS_URL': get_docker_secret('STASIS_URL', default=os.getenv('STASIS_URL',os.getenv('STASIS_API_TOKEN'))),
            'AWS_ACCESS_KEY_ID': get_docker_secret('AWS_ACCESS_KEY_ID', default=current_credentials.access_key),
            'AWS_SECRET_ACCESS_KEY': get_docker_secret('AWS_SECRET_ACCESS_KEY',
                                                       default=current_credentials.secret_key),

        }
