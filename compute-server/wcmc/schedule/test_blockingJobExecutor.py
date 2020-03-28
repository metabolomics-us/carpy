from time import sleep, time
from typing import List

from wcmc.schedule.scheduler import BlockingJobExecutor, Job


class DummyBlockingExecutor(BlockingJobExecutor):
    """
    tests the general behavior of the super class
    """

    def _process(self, sample: str, job: Job):
        pass

    def _wait_for_processing(self, job: Job):
        sleep(2)
        pass

    def _get_successful_samples(self, job: Job) -> List[str]:
        return job.samples

    def _aggregate(self, samples: List[str], job: Job):
        pass


def test_execute():
    job = Job(
        samples=["123", "1234", "`1234"],
        method="test"
    )

    begin = time()
    executor = DummyBlockingExecutor()
    executor.execute(job=job)
    end = time()

    duration = end - begin

    assert duration > 2, "time needs to be at least 2 seconds, since this is the sleep time"
    assert duration < 3, "time needs to be less than 3 seconds, since the sleep time is 2s"
