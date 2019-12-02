from typing import Optional

from wcmc.schedule.scheduler import Scheduler, Job, SampleStateService, JobState, JobStore, SampleState, JobExecutor


class MemoryScheduler(Scheduler):
    """
    non production memory scheduler
    """

    def _get_job_store(self) -> JobStore:
        return self.state_service.job_store

    def set_job_state(self, id: str, state: JobState):
        if id in self.store:
            job = self.store.load(id)
            job = job._replace(state=state)
            self.store[id] = job
        else:
            raise KeyError("sorry job with id {} does not exist!".format(id))

    def job_state(self, id: str) -> JobState:
        if id in self.store:
            return self.store[id].state
        else:
            return JobState.NOT_FOUND

    def __init__(self, executor: JobExecutor):
        super().__init__(executor)
        self.store = self.state_service.job_store

    def _get_state_service(self) -> SampleStateService:
        return MemorySampleStateService()

    def job_cancel(self, id: str):
        self.set_job_state(id, JobState.CANCELLED)


class MemoryJobStore(JobStore):
    """
    simple in memory job store
    """

    def __init__(self):
        self.jobs = {}

    def store(self, job: Job):
        self.jobs[job.generate_id()] = job

    def delete(self, job_id: str):
        self.jobs[job_id] = None

    def load(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id, None)


class MemorySampleStateService(SampleStateService):
    """
    in memory implementation of the state service. This should not be used for production service obviously
    """

    def __init__(self):
        super().__init__()
        self.keeper = {}

    def _get_job_store(self) -> JobStore:
        return MemoryJobStore()

    def set_state(self, id: str, sample_name: str, state: SampleState):
        self.keeper["{}_{}".format(id, sample_name)] = state

    def _state_sample(self, id: str, sample_name: str) -> SampleState:
        key = "{}_{}".format(id, sample_name)

        if key in self.keeper:
            return self.keeper[key]
        else:
            return SampleState.NOT_FOUND
