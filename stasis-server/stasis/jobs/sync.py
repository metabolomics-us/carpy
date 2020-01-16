from typing import Optional

from stasis.jobs.states import States
from stasis.tables import load_job_samples, set_sample_job_state, get_tracked_state, set_job_state, update_job_state, \
    get_job_state


def sync(job: str) -> Optional[States]:
    """
    this method keeps the stasis tracking table and the job tracking in sync.
    """

    # 1. evaluate existing job state
    # to avoid expensive synchronization
    state = get_job_state(job=job)

    if state is None:
        update_job_state(job=job, state=States.SCHEDULED)
    elif state in [States.PROCESSED, States.AGGREGATED, States.AGGREGATED]:
        return state

    # 2. load job definition
    job_definition = load_job_samples(job=job)

    if job_definition is not None:

        # 3. go over all samples

        states = []
        for sample, tracking_state in job_definition.items():

            #  get state
            stasis_state = get_tracked_state(sample=sample)
            # if state is None -> ignore it doesn't exist
            if stasis_state is None:
                print("sample for job {} not found in stasis: {}".format(job, sample))
                pass
            # if state is exported -> set state to processed
            elif stasis_state == "exported" or stasis_state == "finished":
                set_sample_job_state(job=job, sample=sample, state=States.PROCESSED)
                states.append(States.PROCESSED)
            # if state is failed -> set state to failed
            elif stasis_state == "failed":
                set_sample_job_state(job=job, sample=sample, state=States.FAILED)
                states.append(States.FAILED)
            # else set state to processing
            elif stasis_state == "scheduled":
                set_sample_job_state(job=job, sample=sample, state=States.SCHEDULED)
                states.append(States.SCHEDULED)
            else:
                set_sample_job_state(job=job, sample=sample, state=States.PROCESSING)
                states.append(States.PROCESSING)

        if len(states) == 0:
            # bigger issue nothing found to synchronize
            return None
        # 4. sync general job state
        # if any in state processing => set job state to processing
        elif States.PROCESSING in states:
            update_job_state(job=job, state=States.PROCESSING)
            return States.PROCESSING
        elif States.SCHEDULED in states:
            update_job_state(job=job, state=States.SCHEDULED)
        else:
            # if all are either failed or processed => set job state to processed
            update_job_state(job=job, state=States.PROCESSED)
            return States.PROCESSED

    else:
        return None
