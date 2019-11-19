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


class JobStore:
    """
    stores the job and its associated information in the backend of the system
    """

    @abstractmethod
    def store(self, job: Job):
        """
        :param job:
        :return:
        """

    @abstractmethod
    def delete(self, job_id: str):
        """

        :param job_id:
        :return:
        """

    @abstractmethod
    def load(self, job_id: str) -> Job:
        """

        :param job_id:
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


class JobState(Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    DONE = "done"
    CANCELLED = "cancelled"
    NOT_FOUND = "not found"


class SampleStateService:
    """
    utilized to process the state of a sample in the system
    """

    def __init__(self):
        self.job_store = self._get_job_store()

    @abstractmethod
    def _get_job_store(self) -> JobStore:
        """
        associated job store for this service
        :return:
        """

    @abstractmethod
    def set_state(self, id: str, sample_name: str, state: SampleState):
        """
        sets the state of a given sample for a given job in the system
        :param id:
        :param sample_name:
        :param state:
        :return:
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

    def _load_samples(self, id: str) -> List[str]:
        """
        loads all the samples associated with this job id
        :param id:
        :return:
        """
        return self.job_store.load(id).samples

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


class JobExecutor:
    """
    actually executes a job or forwards it to a queue or whatever
    """

    def __init__(self):
        self._scheduler = None

    @property
    def scheduler(self):
        return self._scheduler

    @scheduler.setter
    def scheduler(self, value):
        assert value is not None
        self._scheduler = value

    @abstractmethod
    def execute(self, job: Job):
        """

        :param job:
        :return:
        """
        pass


class Scheduler:
    """
    a simple scheduler to process a list of files
    """

    def __init__(self, executor: JobExecutor):
        """
        :param state_service:
        """
        self.state_service = self._get_state_service()
        self.executor = executor
        executor.scheduler = self

    def submit(self, job: Job):
        """
        submits a job to the quere
        :param job:
        :return:
        """
        self.set_job_state(job.generate_id(), JobState.SCHEDULED)
        self.executor.execute(job)

    @abstractmethod
    def set_job_state(self, id: str, state: JobState):
        """
        used to keep track of the job state
        :param id:
        :param state:
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

    @abstractmethod
    def job_state(self, id: str) -> JobState:
        """
        current state of the job
        :return:
        """

    @abstractmethod
    def _get_state_service(self) -> SampleStateService:
        """
        returns the associated sample state service
        :return:
        """
