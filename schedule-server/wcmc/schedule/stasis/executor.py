from wcmc.schedule.scheduler import JobExecutor, Job, JobState


class StasisExecutor(JobExecutor):
    """
    provides access to the stasis based execution service. It basically submits a job to stasis and
    additionally set the initial state of the process
    """

    def execute(self, job: Job) -> JobState:
        pass