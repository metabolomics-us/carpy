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
            secrets = os.environ
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
        return secrets
