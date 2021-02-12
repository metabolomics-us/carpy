import json
import os
from time import sleep

import yaml
from crag.aws import JobAggregator
from stasis_client.client import StasisClient
from tqdm import tqdm

from lcb.evaluator import Evaluator


class JobEvaluator(Evaluator):

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
        job = self.stasisClient.load_job_state(job_id=id)

        print(json.dumps(job, indent=4))

        return job

    def process(self, id, args):
        result = self.stasisClient.schedule_job(id)

        print("job scheduled for processing: {}".format(result))
        return result

    def exist(self, id, args):
        try:
            result = self.stasisClient.load_job_state(id)
            print("job {} exists: True".format(id))
            return True
        except Exception:
            print("job {} exist: False".format(id))
            return False

    def retrieve(self, id: str, args):

        content = self.stasisClient.download_job_result(job=id)

        if content is None:
            print("did not find a result for '{}' on '{}'".format(id, self.stasisClient.get_aggregated_bucket()))
            state = self.stasisClient.load_job_state(id)
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
        job_state = self.stasisClient.load_job_state(id)

        print("loading job...")
        job = self.stasisClient.load_job(id)

        print(json.dumps(job, indent=4))

        samples = []
        final_state_sample = {}
        failures = {}
        for sample in tqdm(job, desc="loading details for all samples"):
            sample_state = self.stasisClient.sample_state(sample['sample'], full_response=True)
            samples.append(sample_state)
            final_state_sample[sample['sample']] = sample_state['status'][-1]
            if sample_state['status'][-1]['value'] == 'failed':
                failures[sample['sample']] = sample_state['status'][-1]

        result = {
            'job': job_state,
            'samples':
                samples,
            'final_sample_state': final_state_sample,
            "failed": failures
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
                result = self.stasisClient.store_job(job, enable_progress_bar=True)
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

        result = self.stasisClient.load_job_state(id)

        print(result)

        return result

    def wait(self, id, args):
        """
        waits for a specific time of attempts
        """
        print("waiting for job to be in state {}".format(args['wait_for']))
        for x in range(0, args['wait_attempts']):
            try:
                result = self.stasisClient.load_job_state(id)

                print(result)
                if result['job_state'] in args['wait_for']:
                    return True

            except Exception as e:
                print(f"observed error, ignoring it: {e}")
            finally:
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
            result = self.stasisClient.force_sync(id)
            print(result)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def configure_jobs(main_parser, sub_parser):
        """
        configures all the options for handling of jobs
        :param jobs:
        :return:
        """

        parser = sub_parser.add_parser(name="job", help="job based operations")
        parser.add_argument("-i", "--id", help="this is your job id", required=True)

        parser.add_argument("-u", "--upload",
                            help="registers the specified job file in the system in preparation for processing. You steel need to start the processing",
                            type=str, default=False)
        parser.add_argument("-p", "--process",
                            help="this starts the processing of the specified job id in the remote system",
                            action='store_true')
        parser.add_argument("--wait-for", nargs='+',
                            help="which states we want to wait for.", dest='wait_for',
                            type=str, default=False)
        parser.add_argument("--wait-attempts",
                            help="how many attempts we do until we are done waiting for a job",
                            type=int, default=10000, dest='wait_attempts')
        parser.add_argument("--wait-time",
                            help="how long do we wait in seconds between attempts for the wait module",
                            type=int, default=10, dest='wait_time')

        parser.add_argument("-d", "--detail", help="specify this flag to return a detailed report",
                            action='store_true')
        parser.add_argument("-e", "--exist", help="checks if the given job exist", action='store_true')
        parser.add_argument("-s", "--status", help="specify this flag to return the current status",
                            action='store_true')
        parser.add_argument("-r", "--retrieve",
                            help="this downloads the specified job, if available to the specified directory..",
                            type=str, default=False)

        parser.add_argument("--force-sync",
                            help="forces a synchronization of the given job. In case stasis is hanging",
                            action='store_true', dest='force_sync')

        return parser
