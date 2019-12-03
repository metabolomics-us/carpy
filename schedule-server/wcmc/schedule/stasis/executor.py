from abc import ABC
from time import sleep
from typing import List

from wcmc.schedule.scheduler import JobExecutor, Job, JobState, SampleState


class StasisExecutor(JobExecutor, ABC):
    """
    provides access to the stasis based execution service. It basically submits a job to stasis and
    additionally set the initial state of the process
    """

    def _submit_to_stasis(self, sample: str, job: Job):
        """
        submits the given sample to stasis for calculation
        :param sample:
        :return:
        """
        pass

    def _aggregate(self, samples: List[str], job: Job):
        """
        does the actual aggregation
        :param samples:
        :param job:
        :return:
        """
        pass


class BlockingStasisExecutor(StasisExecutor):
    """
    a blocking implementation, which will wait for the dataprocessing to complete remotely
    before it will start with the aggregation.
    """

    def __init__(self):
        super().__init__()
        self.sleep_time = 10

    def execute(self, job: Job) -> JobState:
        """
        does the actual execution and processing of the data in a simple blocking way. Which is far from perfect.

        :param job:
        :return:
        """
        # 1. submit all samples to stasis

        for sample in job.samples:
            self._submit_to_stasis(sample=sample, job=job)
        # 2. wait until processing is done

        while self.scheduler.state_service.processing_done(job.generate_id()) is False:
            sleep(self.sleep_time)

        # 3. aggregate all samples, which are completed and not in the failed state
        to_aggregate = list(
            map(lambda s: self.scheduler.state_service.sample_by_state(sample=s, state=SampleState.PROCESSED)[
                0], job.samples))

        # done
        return JobState.DONE
