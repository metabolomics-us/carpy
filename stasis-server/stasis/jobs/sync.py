import simplejson as json

from stasis.headers import __HTTP_HEADERS__
from stasis.schedule.backend import Backend, DEFAULT_PROCESSING_BACKEND
from stasis.schedule.schedule import schedule_to_queue, _get_queue
from stasis.config import SECURE_CARROT_AGGREGATOR
from stasis.service.Status import *
from stasis.tables import load_job_samples_with_states, update_job_state, \
    get_job_state, load_jobs_for_sample, get_job_config


def sync_sample(sample: str):
    """
    synchronizes all related jobs for this sample
    :param sample:
    :return:
    """
    # get topic refrence
    import boto3
    client = boto3.client('sqs')
    # if topic exists, we just reuse it
    arn = _get_queue(client, resource=Backend.NO_BACKEND_REQUIRED, queue_name="sample_sync_queue")

    jobs = load_jobs_for_sample(sample, id_only=True)

    if jobs is not None:
        print("found {} associated jobs for this sample".format(len(jobs)))
        for job in jobs:
            # submit item to queue for routing to the correct persistence
            print("sending sync request for job {} to queue {}".format(job, arn))
            serialized = json.dumps({'job': job}, use_decimal=True)
            result = client.send_message(
                QueueUrl=arn,
                MessageBody=json.dumps({'default': serialized}),
            )
    else:
        print("no associated job found for sample {}".format(sample))


def do_sync(event, context):
    """
    synchronizes the actual job
    """

    ##
    # sqs trigger
    if 'Records' in event:
        for message in event['Records']:
            print(message)
            body = json.loads(json.loads(message['body'])['default'])

            if 'job' in body:
                job = body['job']
                config = get_job_config(job)
                print("received job to synchronize: {}".format(config))
                sync_job(config)

    ##
    # http trigger
    if 'pathParameters' in event:
        job = event['pathParameters']['job']
        import boto3
        client = boto3.client('sqs')
        arn = _get_queue(client, resource=Backend.NO_BACKEND_REQUIRED, queue_name="sample_sync_queue")

        print("sending sync request for job {} to queue {}".format(job, arn))
        serialized = json.dumps({'job': job}, use_decimal=True)
        result = client.send_message(
            QueueUrl=arn,
            MessageBody=json.dumps({'default': serialized}),
        )
        return {

            'body': json.dumps({'result': str(result), 'job': job}),

            'statusCode': 200,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }


def calculate_job_state(job: str) -> Optional[str]:
    """
    this method keeps the stasis tracking table and the job tracking in sync.
    """

    # 1. evaluate existing job state
    # to avoid expensive synchronization
    state = get_job_state(job=job)

    s = States()
    print("current job state for {} is {}".format(job, state))
    if state is None:
        print(f"no job state found -> forcing scheduled state for {job}")
        update_job_state(job=job, state=SCHEDULED,
                         reason="job was forced to state scheduled due to no state being available!")
    elif s.priority(state) >= s.priority(AGGREGATING_SCHEDULING):
        print(f"job was already in a finished state {job}, state {state} and so needs no further analysis")
        return state
    else:
        print(f"job {job} was in state {state}, which requires it to get it's final state analyzed")

    # 2. load job definition
    # loading all the samples here still causes timeouts or excessive CPU cost todo find a solution
    job_definition = load_job_samples_with_states(job=job)
    job_config = get_job_config(job=job)

    if job_definition is not None and job_config is not None:
        states = []
        try:
            # 3. go over all samples

            for sample, tracking_state in job_definition.items():
                states.append(tracking_state)

            print("received sample states for job are: {}".format(states))
            if len(states) == 0:
                # bigger issue nothing found to synchronize
                print("no states found!")
                return None

            # ALL ARE FAILED
            elif states.count(FAILED) == len(states):
                update_job_state(job=job_config['id'], state=FAILED,
                                 reason="job is in state failed, due to all samples being in state failed")
                print("job is failed, no sample was successful")
                return FAILED
            # ALL ARE EXPORTED OR FAILED
            elif states.count(EXPORTED) + states.count(FAILED) == len(states):
                update_job_state(job=job_config['id'], state=EXPORTED,
                                 reason="job state was set to exported due to all samples having been exported or failed")
                print("job should now be exported")
                return EXPORTED
            # ANY ARE SCHEDULED
            elif states.count(SCHEDULED) == len(states):
                update_job_state(job=job_config['id'], state=SCHEDULED,
                                 reason="job is in state scheduled, due to all samples being in state scheduled")
                print("job still in state scheduled")
                return SCHEDULED

            # otherwise we must be processing
            else:
                update_job_state(job=job_config['id'], state=PROCESSING, reason="job is in state processing")
                print("job is in state processing right now")
                from collections import Counter
                print(Counter(states))
                return PROCESSING
        finally:
            from collections import Counter
            print("state distribution for job '{}' with {} samples is: {}".format(job, len(states), Counter(states)))

    else:
        raise Exception("we did not find a job definition for {}, Please investigate".format(job))


def sync_job(job: dict):
    print("synchronizing job: {}".format(job))
    if job is None:
        result = "warning a none job was provided, we ignore this one!"
    else:
        state = calculate_job_state(job['id'])
        if 'resource' in job:
            resource = Backend(job['resource'])
        else:
            resource = DEFAULT_PROCESSING_BACKEND
        if state == EXPORTED:
            result = "schedule aggregation for job {}, due to state being {}".format(job['id'], state)
            update_job_state(job=job['id'], state=AGGREGATING_SCHEDULING, reason="synchronization triggered")
            schedule_to_queue({"job": job['id'], "profile": job['profile']},
                              service=SECURE_CARROT_AGGREGATOR,
                              resource=resource)
            update_job_state(job=job['id'], state=AGGREGATING_SCHEDULED,
                             reason="synchronization was triggered and completed")
        else:
            result = f"state {state} for job {job['id']} did not justify triggering an aggregation."

    return result
