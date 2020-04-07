import json
import traceback

from boto3.dynamodb.conditions import Key
from jsonschema import validate

from stasis.headers import __HTTP_HEADERS__
from stasis.jobs.states import States
from stasis.jobs.sync import sync
from stasis.schedule.schedule import schedule_to_queue, SECURE_CARROT_RUNNER, SECURE_CARROT_AGGREGATOR, \
    DEFAULT_PROCESSING_BACKEND
from stasis.schema import __JOB_SCHEMA__
from stasis.tables import set_sample_job_state, set_job_state, TableManager, update_job_state, load_job_samples, \
    get_job_config


def store_job(event, context):
    """
    stores a job in the internal database
    :param event:
    :param context:
    :return:
    """

    body = json.loads(event['body'])
    validate(body, __JOB_SCHEMA__)

    job_id = body['id']
    samples = body['samples']
    method = body['method']
    env_ = body['env']
    profile = body['profile']

    if 'resource' in body:
        resource = body['resource']
    else:
        resource = DEFAULT_PROCESSING_BACKEND

    # send to processing queue, might timeout web session for very large jobs
    # refactor later accordingly to let it get processed in a lambda itself to avoid this
    try:

        # store actual job in the job table with state scheduled
        set_job_state(job=job_id, method=method, env=env_, profile=profile,
                      state=States.STORED, resource=resource)
        for sample in samples:
            set_sample_job_state(
                job=job_id,
                sample=sample,
                state=States.STORED
            )
        return {

            'body': json.dumps({'state': str(States.STORED), 'job': job_id}),

            'statusCode': 200,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }
    except Exception as e:
        # update job state in the system to failed with the related reason
        set_job_state(job=job_id, method=method, env=env_, profile=profile,
                      state=States.FAILED, reason=str(e))

        traceback.print_exc()
        return {

            'body': json.dumps({'state': str(States.FAILED), 'job': job_id, 'reason': str(e)}),

            'statusCode': 500,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }


def schedule_job(event, context):
    """
    schedules the job for our processing
    """

    if 'headers' in event and 'x-api-key' in event['headers']:
        stasis_key = event['headers']['x-api-key']
    else:
        stasis_key = None

    job_id = event['pathParameters']['job']

    details = get_job_config(job_id)

    if details is None:
        return {

            'body': json.dumps({'error': 'this job has not been stored yet!', 'job': job_id}),

            'statusCode': 404,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }

    samples = list(load_job_samples(job_id).keys())
    method = details['method']
    env_ = details['env']
    profile = details['profile']

    if 'resource' in details:
        resource = details['resource']
    else:
        resource = DEFAULT_PROCESSING_BACKEND

    # send to processing queue, might timeout web session for very large jobs
    # refactor later accordingly to let it get processed in a lambda itself to avoid this
    try:

        # store actual job in the job table with state scheduled
        set_job_state(job=job_id, method=method, env=env_, profile=profile,
                      state=States.SCHEDULING)
        for sample in samples:
            try:
                schedule_to_queue({
                    "sample": sample,
                    "env": env_,
                    "method": method,
                    "profile": profile,
                    "key": stasis_key
                }, service=SECURE_CARROT_RUNNER, resource=resource)
                set_sample_job_state(
                    job=job_id,
                    sample=sample,
                    state=States.SCHEDULED
                )
            except Exception as e:
                set_sample_job_state(
                    job=job_id,
                    sample=sample,
                    state=States.FAILED,
                    reason=str(e)
                )
        set_job_state(job=job_id, method=method, env=env_, profile=profile,
                      state=States.SCHEDULED)

        return {

            'body': json.dumps({'state': str(States.SCHEDULED), 'job': job_id}),

            'statusCode': 200,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }
    except Exception as e:
        # update job state in the system to failed with the related reason
        set_job_state(job=job_id, method=method, env=env_, profile=profile,
                      state=States.FAILED, reason=str(e))

        traceback.print_exc()
        return {

            'body': json.dumps({'state': str(States.FAILED), 'job': job_id, 'reason': str(e)}),

            'statusCode': 500,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }


def monitor_jobs(event, context):
    """
    monitors the current jobs in the system. It asks the job table for all unfinished jobs
    if they are ready for processing
    """

    # 1. query JOB state table in state running
    tm = TableManager()
    table = tm.get_job_state_table()

    query_params = {
        'IndexName': 'state-index',
        'Select': 'ALL_ATTRIBUTES',
        'KeyConditionExpression': Key('state').eq(str(States.SCHEDULED))
    }

    result = table.query(**query_params)

    if 'Items' in result:
        if len(result['Items']) == 0:
            print("no jobs in state scheduled!")

            query_params = {
                'IndexName': 'state-index',
                'Select': 'ALL_ATTRIBUTES',
                'KeyConditionExpression': Key('state').eq(str(States.PROCESSING))
            }

            result = table.query(**query_params)

        for x in result['Items']:
            try:
                state = sync(x['id'])

                if 'resource' in x:
                    resource = x['resource']
                else:
                    resource = DEFAULT_PROCESSING_BACKEND

                if state == States.PROCESSED:
                    print("schedule aggregation for {}".format(x))
                    schedule_to_queue({"job": x['id'], "env": x['env'], "profile": x['profile']},
                                      service=SECURE_CARROT_AGGREGATOR,
                                      resource=resource)
                    update_job_state(job=x['id'], state=States.AGGREGATION_SCHEDULED)
            except Exception as e:
                traceback.print_exc()
                update_job_state(job=x['id'], state=States.FAILED, reason=str(e))
