from abc import abstractmethod
from datetime import datetime

from stasis_client.client import StasisClient


class Evaluator:
    """
    basic avaulator of command line arguments
    """

    def __init__(self, stasis: StasisClient):
        self.client = stasis

    @abstractmethod
    def evaluate(self, args: dict):
        pass


class SampleEvaluator(Evaluator):
    """
    evaluates received commands from the client
    """

    def __init__(self, stasis: StasisClient):
        super().__init__(stasis)

    def evaluate(self, args: dict):
        """
        :return:
        """
        mapping = {
            'status': self.state,
            'process': self.process,
            'exist': self.exists,
            'retrieve': self.download,
            'detail': self.info,

        }

        results = {}
        for x in mapping.keys():
            if x in args:
                if args[x] is True:
                    results[x] = mapping[x](args['id'], args)
        return results

    def process(self, id, args):
        """

        :param id:
        :return:
        """

        # 1. fetch metadata for sample

        acquistion_data = self.client.sample_acquisition_get(id)
        # 2. schedule

        result = self.client.schedule_sample_for_computation(
            sample_name=id,
            method=acquistion_data['processing']['method'],
            profile=args['profile'],
            env=args['env']
        )

        if result.status_code == 200:
            print("sample was scheduled for processing")
        else:
            print("something went wrong during scheduling")

        pass
        # 3. return

    # pretty print
    def state(self, id, args):
        """

        :param id:
        :return:
        """

        result = self.client.sample_state(sample_name=id)[0]

        priority = result['priority']
        state = result['value']
        timestamp = datetime.fromtimestamp(result['time'])

        print(f"sample {id} current state is {state} and it was entered at {timestamp}")

        return result

    def download(self, id, args):
        """

        :param id:
        :return:
        """

    def info(self, id, args):
        """

        :param id:
        :return:
        """
        acquistion_data = self.client.sample_acquisition_get(id)
        state = self.client.sample_state(sample_name=id)

        pass
        # pretty print

    def exists(self, id, args):
        """

        :param id:
        :return:
        """
