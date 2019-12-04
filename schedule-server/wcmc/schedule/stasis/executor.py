from abc import ABC
from time import sleep
from typing import List

from crag.aggregator import Aggregator
from stasis_client.client import StasisClient

from wcmc.schedule.scheduler import JobExecutor, Job, SampleState, BlockingJobExecutor


class StasisExecutor(JobExecutor, ABC):
    """
    provides access to the stasis based execution service. It basically submits a job to stasis and
    additionally set the initial state of the process
    """

    def __init__(self):
        super().__init__()
        test_mode = True
        self.stasis_cli = StasisClient(f'https://{"test-" if test_mode else ""}api.metabolomics.us/stasis',
                                       None
                                       )

    def _submit_to_stasis(self, sample: str, job: Job):
        """
        submits a sample to stasis
        :param sample:
        :param job:
        :return:
        """


    def _get_stasis_client(self) -> StasisClient:
        """
        provides access to the stasis client for processing
        :return:
        """
        return self.stasis_cli


class BlockingStasisExecutor(BlockingJobExecutor, StasisExecutor):
    """
    a blocking implementation, which will wait for the dataprocessing to complete remotely
    before it will start with the aggregation.
    """

    def _process(self, sample: str, job: Job):
        self._submit_to_stasis(sample=sample, job=job)

    def _aggregate(self, samples: List[str], job: Job):
        aggregator = Aggregator({}, stasis=self._get_stasis_client())
        aggregator.aggregate_samples(samples=samples, destination=self.destination)

    def _wait_for_processing(self, job: Job):
        while self.scheduler.state_service.processing_done(job.generate_id()) is False:
            sleep(self.sleep_time)

    def _get_successful_samples(self, job: Job) -> List[str]:
        to_aggregate = list(
            map(lambda s: self.scheduler.state_service.sample_by_state(sample=s, state=SampleState.PROCESSED)[
                0], job.samples))

        return to_aggregate

    def __init__(self):
        super().__init__()
        self.sleep_time = 10
        self.destination = "./"
