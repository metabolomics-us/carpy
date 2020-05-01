import json

from stasis_client.client import StasisClient

from lcb.evaluator import Evaluator


class JobEvaluator(Evaluator):

    def __init__(self, stasis: StasisClient):
        super().__init__(stasis)

    def evaluate(self, args: dict):
        mapping = {
            'status': self.status,
            'process': self.process,
            'exist': self.exist,
            'retrieve': self.retrieve,
            'detail': self.detail,
            'upload': self.upload,
            'aggregate': self.aggregate,
            'monitor': self.monitor,
        }

        results = {}
        for x in mapping.keys():
            if x in args:
                if args[x] is not False:
                    results[x] = mapping[x](args['id'], args)
        return results

    def status(self, id, args):
        job = self.client.load_job_state(job_id=id)

        print(json.dumps(job, indent=4))

        return job

    def process(self, id, args):
        result = self.client.schedule_job(id)

        print("job scheduled for processing: {}".format(result))
        return result

    def exist(self, id, args):
        try:
            result = self.client.load_job_state(id)
            print("job {} exists: True".format(id))
            return True
        except Exception:
            print("job {} exist: False".format(id))
            return False

    def retrieve(self, id, args):
        pass
        assert False

    def detail(self, id, args):
        job_state = self.client.load_job_state(id)
        job = self.client.load_job(id)

        samples = []
        for sample in job:
            samples.append(self.client.sample_state(sample['sample'], full_response=True))
        result = {
            'job': job_state,
            'samples':
                samples

        }

        print("details are")
        print(json.dumps(result, indent=4))
        return result

    def upload(self, id, args):
        """
        uploads a new job to the server for storage and future processing
        """
        with open(args['upload'], 'r') as infile:
            job = json.load(infile)
            job['id'] = id

            try:
                print("uploading job")
                print(json.dumps(job, indent=4))
                result = self.client.store_job(job, enable_progress_bar=True)
                print("done")
                print("complete job")
                print(self.detail(id, {}))
                return True
            except Exception as e:
                print("input caused error:\n")
                print(json.dumps(job, indent=4))
                print(f"\nerror was: {str(e)}")
                return False

    def aggregate(self, id, args):
        pass
        assert False

    def monitor(self, id, args):
        """
        monitors the state of a specified job
        :param id:
        :param args:
        :return:
        """

        result = self.client.load_job_state(id)

        print(result)

        return result
