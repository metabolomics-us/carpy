import json
from datetime import datetime

from lcb.evaluator import Evaluator


class SampleEvaluator(Evaluator):
    """
    evaluates received commands from the client
    """

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
            'full': self.record,

        }

        results = {}
        for x in mapping.keys():
            if x in args:
                if args[x] is not False:
                    results[x] = mapping[x](args['id'], args)
        return results

    def process(self, id, args):
        """

        :param id:
        :return:
        """

        # 1. fetch metadata for sample

        acquistion_data = self.stasisClient.sample_acquisition_get(id)
        # 2. schedule

        print()
        result = self.stasisClient.schedule_sample_for_computation(
            sample_name=id,
            method=acquistion_data['processing']['method'],
            profile=args['profile'],
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

        result = self.stasisClient.sample_state(sample_name=id, full_response=True)

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

        result = self.stasisClient.sample_result_as_json(sample_name=id)

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
            acquistion_data = self.stasisClient.sample_acquisition_get(id)
            state = self.stasisClient.sample_state(sample_name=id)

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
            acquistion_data = self.stasisClient.sample_acquisition_get(id)
            state = self.stasisClient.sample_state(sample_name=id)
            processing_result = self.stasisClient.sample_result_as_json(sample_name=id)
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
        self.stasisClient

    @staticmethod
    def configure_samples(main_parser, sub_parser):
        """
        configures all the options for a sample parser
        :param sample_parser:
        :return:
        """

        parser = sub_parser.add_parser(name="sample", help="sample based operations")
        parser.add_argument("-i", "--id", help="this is your sample id or name", required=True)
        parser.add_argument("-s", "--status", help="specify this flag to return the current status",
                            action='store_true')
        parser.add_argument("-p", "--process", help="this starts the processing of the specified sample",
                            action='store_true')
        parser.add_argument("-r", "--retrieve", help="this downloads the specified sample result", action='store_true')
        parser.add_argument("-f", "--full",
                            help="this downloads the specified sample result and all associated metadata",
                            action='store_true')
        parser.add_argument("-e", "--exist", help="checks if the given sample exist", action='store_true')
        parser.add_argument("-d", "--detail", help="provides a complete detailed view of the sample",
                            action='store_true')
        parser.add_argument("--profile", help="which profile to utilize for scheduling", default="lcms", required=False)
        parser.add_argument("--env", help="which env to utilize for scheduling", default="test", required=False)

        return parser
