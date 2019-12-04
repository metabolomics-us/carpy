from stasis_client.client import StasisClient

from wcmc.schedule.scheduler import SampleStateService, SampleState, JobStore


class StasisSampleStateService(SampleStateService):
    """
    utilizes stasis to keep track of sample states of the scheduled jobs.
    """

    def __init__(self, job_store: JobStore):
        super().__init__(job_store)
        self.stasis_cli = StasisClient()

        self.stasis_states = self.stasis_cli.get_states()

        # static mapping to the stasis states
        self.state_map = {
            SampleState.PROCESSED: self.stasis_states['exported'],
            SampleState.FAILED: self.stasis_states['failed'],
            SampleState.SCHEDULED: self.stasis_states['entered']

        }

    def set_state(self, id: str, sample_name: str, state: SampleState):
        pass

    def _state_sample(self, id: str, sample_name: str) -> SampleState:
        pass
