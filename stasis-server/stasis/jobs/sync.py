from typing import Optional

from stasis.service.Status import *
from stasis.tables import load_job_samples, update_job_state, \
    get_job_state


def sync(job: str) -> Optional[str]:
    """
    this method keeps the stasis tracking table and the job tracking in sync.
    """

    # 1. evaluate existing job state
    # to avoid expensive synchronization
    state = get_job_state(job=job)

    print("current job state for {} is {}".format(job,state))
    if state is None:
        print(f"no job state found -> forcing scheduled state for {job}")
        update_job_state(job=job, state=SCHEDULED)
    elif state in [AGGREGATED, FAILED]:
        print(f"job was already in a finished state {job}, state {state} and so needs no further analysis")
        return state

    # 2. load job definition
    job_definition = load_job_samples(job=job)

    if job_definition is not None:

        # 3. go over all samples

        states = []
        for sample, tracking_state in job_definition.items():
            states.append(tracking_state)

        if len(states) == 0:
            # bigger issue nothing found to synchronize
            return None

        # ALL ARE EXPORTED OR FAILED
        elif states.count(EXPORTED) + states.count(FAILED) == len(states):
            update_job_state(job=job, state=EXPORTED)
            return EXPORTED
        # ANY ARE SCHEDULED
        elif states.count(SCHEDULED) == len(states):
            update_job_state(job=job, state=SCHEDULED)
            return SCHEDULED
        # ALL ARE FAILED
        elif states.count(FAILED) == len(states):
            update_job_state(job=job, state=FAILED)
            return FAILED
        # otherwise we must be processing
        else:
            update_job_state(job=job, state=PROCESSING)
            return PROCESSING
    else:
        print("we did not find a job definition for {}, Please investigate".format(job))
        return None
