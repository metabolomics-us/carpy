class StasisClient:
    """
    a simple client to interact with the stasis system in a safe and secure manner.
    """

    def __init__(self, url: str, token: str):
        """
        the client requires an url where to connect against
        and the related token.

        :param url:
        :param token:
        """

        self._url = url
        self._token = token

    def sample_state(self, sample_name: str):
        """
        returns the state of the given sample
        :param sample_name:
        :return:
        """
        pass

    def sample_result(self, sample_name: str):
        """
        returns the result for a specified sample
        :param sample_name:
        :return:
        """
        pass

    def sample_schedule(self, sample_name: str, method: str, mode: str):
        """
        schedules a sample for calculation
        :param sample_name:
        :param method:
        :param mode:
        :return:
        """

    def sample_exist(self, sample_name) -> bool:
        """
        does this given sample exist in the system or not
        :param sample_name:
        :return:
        """

    def sample_metadata(self, sample_name):
        """
        the associated metadata for a given sample
        :param sample_name:
        :return:
        """

    def experiment_samples(self, experiment_id):
        """
        returns all samples of a given experiment
        :param experiment_id:
        :return:
        """
