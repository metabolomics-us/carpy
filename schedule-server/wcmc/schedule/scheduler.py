from abc import abstractmethod
from enum import Enum
from typing import NamedTuple, List


class Job(NamedTuple):
    """
    defines a data processing job
    """

    # name of the method to use
    method: str

    # list of the samples to process
    samples: List[str]

    # list of email address who to notify
    to_notify: List[str]

    def generate_id(self) -> str:
        """
        this generates an unique id for this given job, based on it's data
        :return:
        """


class SampleState(Enum):
    """
    state of a given sample
    """
    SCHEDULED = "scheduled"
    DONE = "done"
    FAILED = "failed"
    PROCESSED = "processed"
    AGGREGATED = "aggregated"


class SampleStateService:
    """
    utilized to process the state of a sample in the system
    """

    def _state(self, id: str) -> List[SampleState]:
        """
        this computes the state for every sample for the given job id
        :param id:
        :param samples:
        :return:
        """
        samples = self._load_samples(id)
        return list(map(lambda sample: self._state_sample(id, sample), samples))

    @abstractmethod
    def _load_samples(self, id: str) -> List[str]:
        """
        loads all the samples associated with this job id
        :param id:
        :return:
        """

    @abstractmethod
    def _state_sample(self, id: str, sample_name: str) -> SampleState:
        """
        conmputes the state of the given sample
        :param id:
        :param sample_name:
        :return:
        """

    def processing_done(self, id: str) -> bool:
        """
        is the processing of the samples for the given job done
        :param id:
        :return:
        """
        return self._is_state_done(id, SampleState.PROCESSED)

    def _is_state_done(self, id: str, state: SampleState) -> bool:
        """
        computes if the given state of this job is done
        :param id:
        :param state:
        :return:
        """
        sample_state = self._state(id)
        samples = self._load_samples(id)
        count = len(samples)
        count_done = sum(1 for x in sample_state if x in [state, SampleState.FAILED])
        return count == count_done

    def aggregation_done(self, id: str) -> bool:
        """
        is the processing of the samples for the given job done
        :param id:
        :return:
        """
        return self._is_state_done(id, SampleState.AGGREGATED)


class Scheduler:
    """
    a simple scheduler to process a list of files
    """

    def __init__(self, state_service: SampleStateService):
        """
        :param state_service:
        """
        self.state_service = state_service

    @abstractmethod
    def submit(self, job: Job):
        """
        submits a job to the quere
        :param job:
        :return:
        """

    def cancel(self, job: Job):
        """
        cancels a given job from the system
        :param job:
        :return:
        """
        self.job_cancel(job.generate_id())

    @abstractmethod
    def job_cancel(self, id: str):
        """
        cancels the job with the given id
        :param id:
        :return:
        """

    def done(self, job: Job) -> bool:
        """
        returns the current state of a job
        :param job:
        :return:
        """
        return self.job_done(job.generate_id())

    def job_done(self, id: str) -> bool:
        """
        computes the correct id and returns the state of a job
        :param id:
        :return:
        """
        return self.state_service.processing_done(id)
