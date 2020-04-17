import json
from typing import Optional

from stasis.schedule.backend import Backend, DEFAULT_PROCESSING_BACKEND
from stasis.schedule.schedule import schedule_to_queue, SECURE_CARROT_AGGREGATOR
from stasis.service.Status import *
from stasis.tables import load_job_samples, update_job_state, \
    get_job_state, load_jobs_for_sample, get_job_config


def sync_sample(sample: str):
    """
    synchronizes all related jobs for this sample
    :param sample:
    :return:
    """
    jobs = load_jobs_for_sample(sample)

    if jobs is not None:
        print("found {} associated jobs for this sample".format(len(jobs)))
        for job in jobs:
            sync_job(job=job)


def calculate_job_state(job: str) -> Optional[str]:
    """
    this method keeps the stasis tracking table and the job tracking in sync.
    """

    # 1. evaluate existing job state
    # to avoid expensive synchronization
    state = get_job_state(job=job)

    print("current job state for {} is {}".format(job, state))
    if state is None:
        print(f"no job state found -> forcing scheduled state for {job}")
        update_job_state(job=job, state=SCHEDULED)
    elif state in [AGGREGATED, FAILED]:
        print(f"job was already in a finished state {job}, state {state} and so needs no further analysis")
        return state

    # 2. load job definition
    job_definition = load_job_samples(job=job)
    job_config = get_job_config(job=job)

    if job_definition is not None:

        # 3. go over all samples

        states = []
        for sample, tracking_state in job_definition.items():
            states.append(tracking_state)

        print("received sample states for job are:")
        print(json.dumps(states, indent=4))
        if len(states) == 0:
            # bigger issue nothing found to synchronize
            print("no states found!")
            return None

        # ALL ARE EXPORTED OR FAILED
        elif states.count(EXPORTED) + states.count(FAILED) == len(states):
            update_job_state(job=job_config['id'], state=EXPORTED)
            print("job should now be exported")
            return EXPORTED
        # ANY ARE SCHEDULED
        elif states.count(SCHEDULED) == len(states):
            update_job_state(job=job_config['id'], state=SCHEDULED)
            print("job still in state scheduled")
            return SCHEDULED
        # ALL ARE FAILED
        elif states.count(FAILED) == len(states):
            update_job_state(job=job_config['id'], state=FAILED)
            print("job is failed, no sample was successful")
            return FAILED
        # otherwise we must be processing
        else:
            update_job_state(job=job_config['id'], state=PROCESSING)
            print("job is in state processing right now")
            return PROCESSING
    else:
        raise Exception("we did not find a job definition for {}, Please investigate".format(job))


def sync_job(job):
    state = calculate_job_state(job['id'])
    if 'resource' in job:
        resource = Backend(job['resource'])
    else:
        resource = DEFAULT_PROCESSING_BACKEND
    if state == EXPORTED:
        print("schedule aggregation for job {}".format(job['id']))
        update_job_state(job=job['id'], state=AGGREGATING_SCHEDULING)
        schedule_to_queue({"job": job['id'], "env": job['env'], "profile": job['profile']},
                          service=SECURE_CARROT_AGGREGATOR,
                          resource=resource)
        update_job_state(job=job['id'], state=AGGREGATING_SCHEDULING)
    else:
        print(f"state {state} for job {job['id']} did not justify triggering an aggregation.")
