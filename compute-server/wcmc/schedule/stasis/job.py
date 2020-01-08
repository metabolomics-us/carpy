from wcmc.schedule.scheduler import JobStore, Job


class AWSJobStore(JobStore):
    def store(self, job: Job):
        pass

    def delete(self, job_id: str):
        pass

    def load(self, job_id: str) -> Job:
        pass