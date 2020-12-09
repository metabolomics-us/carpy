import os
import json

from boto3 import Session, setup_default_session
from get_docker_secret import get_docker_secret


class Secrets:
    """
    helper class to provides us with a dict of all the system wide secrets, depending if it runs inside of docker
    or inside the os
    """

    def load(self) -> dict:

        s = get_docker_secret("node")

        if s is None:
            secrets = dict(os.environ)
        else:
            secrets = json.loads(s)

        try:
            session = Session()
            credentials = session.get_credentials()
            current_credentials = credentials.get_frozen_credentials()

            key = current_credentials.secret_key
            access = current_credentials.access_key

            secrets['AWS_ACCESS_KEY_ID'] = access
            secrets['AWS_SECRET_ACCESS_KEY'] = key
        except Exception as e:
            pass

        # configure default boto session here
        setup_default_session(aws_access_key_id=secrets['AWS_ACCESS_KEY_ID'],
                              aws_secret_access_key=secrets['AWS_SECRET_ACCESS_KEY'], region_name="us-west-2")

        self.fix_old_variable_names(secrets)

        return secrets

    def fix_old_variable_names(self, secrets):
        """
        fixes the old naming convention to the new ones, which is simpler. Mostly related to outdated configurations
        """
        # fix stupid naming errors
        if 'STASIS_API_TOKEN' in secrets:
            secrets['STASIS_TOKEN'] = secrets['STASIS_API_TOKEN']
        if 'STASIS_API_URL' in secrets:
            secrets['STASIS_URL'] = secrets['STASIS_API_URL']
        if 'CIS_API_TOKEN' in secrets:
            secrets['CIS_TOKEN'] = secrets['CIS_API_TOKEN']
        if 'CIS_API_URL' in secrets:
            secrets['CIS_URL'] = secrets['CIS_API_URL']
        if 'CIS_TOKEN' not in secrets:
            secrets['CIS_TOKEN'] = secrets['STASIS_TOKEN']
        if 'CIS_URL' not in secrets:
            secrets['CIS_URL'] = secrets['STASIS_URL'].replace("/stasis", "/cis")
