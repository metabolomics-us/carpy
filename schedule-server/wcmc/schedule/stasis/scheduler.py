from wcmc.schedule.scheduler import Scheduler, JobStore, SampleStateService, JobState, JobExecutor
from wcmc.schedule.stasis.job import AWSJobStore
from wcmc.schedule.stasis.state import StasisSampleStateService


class AWSScheduler(Scheduler):
    """
    utilizes AWS as scheduling service
    """

    def set_job_state(self, id: str, state: JobState):
        pass

    def job_cancel(self, id: str):
        pass

    def job_state(self, id: str) -> JobState:
        pass

    def _get_state_service(self, job_store: JobStore) -> SampleStateService:
        return StasisSampleStateService(job_store=job_store)

    def _get_job_store(self) -> JobStore:
        return AWSJobStore()
