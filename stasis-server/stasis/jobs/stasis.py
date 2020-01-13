from typing import Optional

from boto3.dynamodb.conditions import Key

from stasis.jobs.states import States
from stasis.tables import TableManager, load_job, set_job_state


def sync(job: str):
    """
    this method keeps the stasis tracking table and the job tracking in sync.
    """

    # 1. load job definition

    job_definition = load_job(job=job)

    if job_definition is not None:

        # 2. go over all samples

        for sample, tracking_state in job_definition.items():

            #  get state
            stasis_state = get_state(sample=sample)
            # if state is None -> ignore it doesn't exist
            if stasis_state is None:
                print("sample for job {} not found in stasis: {}".format(job, sample))
                pass
            # if state is exported -> set state to processed
            elif stasis_state == "exported" or stasis_state == "finished":
                set_job_state(job=job, sample=sample, state=States.PROCESSED)
            # if state is failed -> set state to failed
            elif stasis_state == "failed":
                set_job_state(job=job, sample=sample, state=States.FAILED)
            # else set state to processing
            else:
                set_job_state(job=job, sample=sample, state=States.PROCESSING)


def get_sample(sample: str) -> Optional[dict]:
    """
    this returns the complete sample definition for the given sample or none from the stasis tracking table
    this is the heart of the synchronization system
    """

    tm = TableManager()
    table = tm.get_tracking_table()

    result = table.query(
        KeyConditionExpression=Key('id').eq(sample)
    )

    if 'Items' in result and len(result['Items']) > 0:
        return result['Items'][0]
    else:
        return None


def get_state(sample: str) -> Optional[str]:
    """
    returns the state of a sample in stasis
    """

    data = get_sample(sample)
    states = data['status']
    state = states[-1]
    if data is None:
        return None
    else:
        return state['value']
