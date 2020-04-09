import json
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


class JobEvaluator(Evaluator):
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
            'full': self.record

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

        print()
        result = self.client.schedule_sample_for_computation(
            sample_name=id,
            method=acquistion_data['processing']['method'],
            profile=args['profile'],
            env=args['env']
        )

        print("sample was scheduled for processing")

        pass
        # 3. return

    # pretty print
    def state(self, id, args):
        """

        :param id:
        :return:
        """

        result = self.client.sample_state(sample_name=id, full_response=True)

        for x in result['status']:
            timestamp = datetime.fromtimestamp(x['time'] / 1000)
            x['date'] = timestamp.strftime("%m/%d/%Y, %H:%M:%S")

        print(json.dumps(result, indent=4))

        return result

    def download(self, id, args):
        """

        :param id:
        :return:
        """

        result = self.client.sample_result_as_json(sample_name=id)

        with open("{}.json".format(id), 'w') as file:
            json.dump(result, file, indent=4)

        print("stored result at {}.json".format(id))

    def info(self, id, args):
        """

        :param id:
        :return:
        """
        print()
        try:
            acquistion_data = self.client.sample_acquisition_get(id)
            state = self.client.sample_state(sample_name=id)

            result = {
                'meta': acquistion_data,
                'state': state
            }

            print(json.dumps(result, indent=4))
        except Exception as e:
            print("exception observed during query for sample {}.\nThe exact message is: {}".format(id, e))

    def record(self, id, args):
        """

        :param id:
        :return:
        """
        print()
        try:
            acquistion_data = self.client.sample_acquisition_get(id)
            state = self.client.sample_state(sample_name=id)
            processing_result = self.client.sample_result_as_json(sample_name=id)
            result = {
                'meta': acquistion_data,
                'state': state,
                'processed': processing_result
            }

            with open("{}.record.json".format(id), 'w') as file:
                json.dump(result, file, indent=4)
            print("stored result at {}.record.json".format(id))

        except Exception as e:
            print("exception observed during query for sample {}.\nThe exact message is: {}".format(id, e))

    def exists(self, id, args):
        """

        :param id:
        :return:
        """
        pass
