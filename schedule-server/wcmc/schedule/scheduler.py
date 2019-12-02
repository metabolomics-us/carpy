import hashlib
from abc import abstractmethod
from enum import Enum
from typing import NamedTuple, List, Optional, Tuple


class JobState(Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    DONE = "done"
    CANCELLED = "cancelled"
    NOT_FOUND = "not found"
    FAILED = "failed"


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

    state: Optional[JobState] = None

    def generate_id(self) -> str:
        """
        this generates an unique id for this given job, based on it's data
        :return:
        """

        return str(hashlib.sha224(
            "{}-{}".format(self.samples, self.method).encode(
                "utf-8")).hexdigest())


class JobBuilder:
    """
    utility class to easily load job definitions
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

    def __setitem__(self, key, value: Job):
        return self.store(value)

    def __getitem__(self, item):
        return self.load(item)

    def __contains__(self, item: str):
        return self.load(item) is not None


class SampleState(Enum):
    """
    state of a given sample
    """
    SCHEDULED = "scheduled"
    DONE = "done"
    FAILED = "failed"
    PROCESSED = "processed"
    AGGREGATED = "aggregated"
    NOT_FOUND = "not found"


class SampleStateService:
    """
    utilized to process the state of a sample in the system
    """

    def __init__(self, job_store: JobStore):
        self.job_store = job_store

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
        return list(map(lambda sample: sample[1], self.sample_by_state(id, state=None)))

    def sample_by_state(self, id: str, state: Optional[SampleState] = None) -> List[Tuple[str, SampleState]]:
        """
        this computes the state for every sample for the given job id
        :param id:
        :param state:
        :return:
        """
        samples = self._load_samples(id)

        result = list(map(lambda sample: (sample, self._state_sample(id, sample)), samples))

        if state is None:
            return result
        else:
            return list(filter(lambda sample: sample[1] == state, result))

    def _load_samples(self, id: str) -> List[str]:
        """
        loads all the samples associated with this job id
        :param id:
        :return:
        """
        job = self.job_store.load(id)

        if job is None:
            return []

        return job.samples

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
        if self._is_state_done(id, SampleState.PROCESSED) is True:
            return True
        if self._is_state_done(id, SampleState.FAILED) is True:
            return True

        return False

    def _is_state_done(self, id: str, state: SampleState) -> bool:
        """
        computes if the given state of this job is done
        :param id:
        :param state:
        :return:
        """
        if self.job_store.load(id) is None:
            return False

        if self.job_store.load(id).state in [JobState.DONE]:
            return True

        sample_state = self._state(id)
        samples = self._load_samples(id)
        count = len(samples)
        count_done = sum(1 for x in sample_state if x in [state, SampleState.FAILED, SampleState.DONE])
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
        self._scheduler: Optional[Scheduler] = None

    @property
    def scheduler(self):
        return self._scheduler

    @scheduler.setter
    def scheduler(self, value):
        assert value is not None
        self._scheduler = value

    @abstractmethod
    def execute(self, job: Job) -> JobState:
        """

        :param job:
        :return: the job state
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
        self.job_store = self._get_job_store()
        assert self.job_store is not None, "job store cannot be none!"
        self.state_service = self._get_state_service(self.job_store)

        assert self.state_service is not None, "state service cannot be none!"
        self.executor = executor
        assert self.executor is not None, "executor cannot be none!"
        executor.scheduler = self

    def submit(self, job: Job):
        """
        submits a job to the quere
        :param job:
        :return:
        """
        try:
            self.job_store.store(job)
            self.set_job_state(job.generate_id(), self.executor.execute(job))
        except Exception as e:
            self.set_job_state(job.generate_id(), JobState.FAILED)
            raise e

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
        if self.state_service.processing_done(id) is True:
            if self.state_service.aggregation_done(id) is True:
                return True
        return False

    @abstractmethod
    def job_state(self, id: str) -> JobState:
        """
        current state of the job
        :return:
        """

    @abstractmethod
    def _get_state_service(self, job_store: JobStore) -> SampleStateService:
        """
        returns the associated sample state service
        :return:
        """

    @abstractmethod
    def _get_job_store(self) -> JobStore:
        """
        how are jobs stored in the internal data
        :return:
        """
