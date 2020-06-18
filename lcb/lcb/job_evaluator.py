import json
import os
from time import sleep

import yaml
from crag.aws import JobAggregator
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
            'wait_for': self.wait,
            'force_sync': self.force_sync,
        }

        results = {}

        for x in args.keys():
            if x in mapping:
                if args[x] is not False or str(args[x]) != 'False':
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

    def retrieve(self, id: str, args):

        content = self.client.download_job_result(job=id)

        if content is None:
            print("did not find a result for '{}' on '{}'".format(id, self.client.get_aggregated_bucket()))
            state = self.client.load_job_state(id)
            print("jobs current state is")
            print(json.dumps(state, indent=4))
            return False
        else:

            outdir = args['retrieve']

            os.makedirs(outdir, exist_ok=True)
            decoded = content

            outfile = "{}/{}.zip".format(outdir, id)
            print("storing result at: {}".format(outfile))
            with open(outfile, 'wb') as out:
                out.write(decoded)
            return True

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

        filename: str = args['upload']

        with open(filename, 'r') as infile:
            if filename.endswith(".json"):
                job = json.load(infile)
            elif filename.endswith(".yml") or filename.endswith(".yaml"):
                job = yaml.load(infile)
            else:
                raise Exception("none supported file extension provided. Extension was: {}".format(filename))

            job['id'] = id

            try:
                print("uploading job")
                print(json.dumps(job, indent=4))
                result = self.client.store_job(job, enable_progress_bar=True)
                print("done")
                return True
            except Exception as e:
                print("input caused error:\n")
                print(json.dumps(job, indent=4))
                print(f"\nerror was: {str(e)}")
                return False

    def aggregate(self, id, args):

        arguments = {
            'job': id,
            'zero_replacement': True,
            'upload': False,
            'mz_tolerance': 0.01,
            'rt_tolerance': 0.1,
        }
        JobAggregator(arguments).aggregate_job(job=id, upload=False)

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

    def wait(self, id, args):
        """
        waits for a specific time of attempts
        """
        print("waiting for job to be in state {}".format(args['wait_for']))
        for x in range(0, args['wait_attempts']):
            result = self.client.load_job_state(id)

            print(result)
            if result['job_state'] in args['wait_for']:
                return True

            sleep(args['wait_time'])

        return False

    def force_sync(self, id, args):
        """
        forces the synchronization of a job
        :param id:
        :param args:
        :return:
        """

        print(f"forcing synchronization of job {id}")
        try:
            result = self.client.force_sync(id)
            print(result)
            return True
        except Exception as e:
            print(e)
            return False
