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
            'aggregate': self.aggregate

        }

        results = {}
        for x in mapping.keys():
            if x in args:
                if args[x] is True:
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
            samples.append(self.client.sample_state(sample, full_response=True))
        result = {
            'job': job_state,
            'samples': {
                samples
            }
        }
        return result

    def upload(self, id, args):
        pass
        assert False

    def aggregate(self, id, args):
        pass
        assert False
