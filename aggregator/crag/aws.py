from typing import Optional

import boto3
from stasis_client.client import StasisClient

from crag.aggregator import Aggregator, NoSamplesFoundException

import shutil


class JobAggregator(Aggregator):
    """
    class to easily aggregate complete jobs, which are stored on the AWS based stasis server
    """

    def __init__(self, args: dict, stasis: Optional[StasisClient] = None):
        """
        specific implementation of a AWS Aggregator
        :param aggregator:
        """
        super().__init__(args, stasis)

    def aggregate_job(self, job: str, upload: bool = True) -> bool:
        """
        aggregates the specific job for us
        :param job:
        :return:
        """
        # 1. load job definition from stasis
        job_data = self.stasis_cli.load_job(job)

        # directory
        directory = "result/{}".format(job)
        # 2. generate sample list which are finished
        samples = list(map(lambda x: x['sample'], filter(lambda x: x['state'] != 'failed', job_data)))

        # 3. aggregate
        try:
            self.aggregate_samples(samples, directory)

            if upload:
                print("zipping data and uploading it to the result bucket...")
                shutil.make_archive(f"result/{job}", 'zip', directory)

                bucket_name = self.stasis_cli.get_result_bucket()
                try:
                    boto3.client('s3').create_bucket(Bucket=bucket_name,
                                                     CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
                except Exception as e:
                    print("sorry this bucket caused an error - this mean it exist, no reason to worry")

                boto3.client('s3').upload_file(f"result/{job}.zip", bucket_name, f"{job}.zip")

            return True
        except NoSamplesFoundException:
            return False
