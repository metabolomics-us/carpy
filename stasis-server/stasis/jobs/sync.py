from stasis.jobs.states import States
from stasis.tables import load_job_samples, set_sample_job_state, get_tracked_state


def sync(job: str):
    """
    this method keeps the stasis tracking table and the job tracking in sync.
    """

    # 1. load job definition

    job_definition = load_job_samples(job=job)

    if job_definition is not None:

        # 2. go over all samples

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
            # if state is failed -> set state to failed
            elif stasis_state == "failed":
                set_sample_job_state(job=job, sample=sample, state=States.FAILED)
            # else set state to processing
            else:
                set_sample_job_state(job=job, sample=sample, state=States.PROCESSING)

