from wcmc.schedule.scheduler import SampleStateService, SampleState, JobStore


class StasisSampleStateService(SampleStateService):
    """
    utilizes stasis to keep track of sample states of the scheduled jobs.
    """

    def set_state(self, id: str, sample_name: str, state: SampleState):
        pass

    def _state_sample(self, id: str, sample_name: str) -> SampleState:
        pass
