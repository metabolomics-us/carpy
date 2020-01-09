from typing import Optional


def sync(job: str):
    """
    this method keeps the stasis tracking table and the job tracking in sync.
    """

    # 1. load job definition

    # 2. go over all samples

    # 3. get state

    # 4. if state is exported -> set state to processed

    # 5. if state is failed -> set state to failed

    # 6. if state is None -> ignore it doesn't exist

    # 7. else return state to processing


def get_sample(sample: str) -> Optional[dict]:
    """
    this returns the complete sample definition for the given sample or none from the stasis tracking table
    this is the heart of the synchronization system
    """


def get_state(sample: str) -> Optional[str]:
    """
    returns the state of a sample in stasis
    """

    data = get_sample(sample)

    if data is None:
        return None
    else:
        return "exported"

