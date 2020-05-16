from collections import Counter

from stasis_client.client import StasisClient


class Utility:
    """
    utility class using the client directly for some calculations
    which are considered useful
    """

    def __init__(self, client: StasisClient):
        """
        init
        """
        self.client = client

    def state_distribution(self, job: str) -> Counter:
        """
        computes a simple state distribution of all samples in a given job
        which should give the user some information where things are right now
        """

        samples = self.client.load_job(job)

        samples = list(map(lambda x: x['state'], samples))
        result = Counter(samples)

        return result
