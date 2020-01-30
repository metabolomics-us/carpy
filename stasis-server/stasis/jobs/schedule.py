import json
import traceback

from boto3.dynamodb.conditions import Key
from jsonschema import validate

from stasis.jobs.states import States
from stasis.jobs.sync import sync
from stasis.schedule.schedule import schedule_to_queue, SECURE_CARROT_RUNNER, SECURE_CARROT_AGGREGATOR
from stasis.schema import __JOB_SCHEMA__
from stasis.tables import set_sample_job_state, set_job_state, TableManager, update_job_state

from stasis.headers import __HTTP_HEADERS__


def schedule_job(event, context):
    """
    schedules the job for our processing
    """

    body = json.loads(event['body'])

    if 'headers' in event and 'x-api-key' in event['headers']:
        stasis_key = event['headers']['x-api-key']
    else:
        stasis_key = None

    validate(body, __JOB_SCHEMA__)

    job_id = body['id']
    samples = body['samples']
    method = body['method']
    env_ = body['env']
    profile = body['profile']
    task_version = body.get('task_version')

    # send to processing queue, might timeout web session for very large jobs
    # refactor later accordingly to let it get processed in a lambda itself to avoid this
    try:

        # store actual job in the job table with state scheduled
        set_job_state(job=job_id, method=method, env=env_, profile=profile, task_version=task_version,
                      state=States.SCHEDULING)
        for sample in samples:
            try:
                schedule_to_queue({
                    "sample": sample,
                    "env": env_,
                    "method": method,
                    "profile": profile,
                    "task_version": task_version,
                    "key": stasis_key
                }, service=SECURE_CARROT_RUNNER)
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
        set_job_state(job=job_id, method=method, env=env_, profile=profile, task_version=task_version,
                      state=States.SCHEDULED)

        return {

            'body': json.dumps({'state': str(States.SCHEDULED), 'job': job_id}),

            'statusCode': 200,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }
    except Exception as e:
        # update job state in the system to failed with the related reason
        set_job_state(job=job_id, method=method, env=env_, profile=profile, task_version=task_version,
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
        'KeyConditionExpression': Key('state').eq(str(States.PROCESSED))
    }

    result = table.query(**query_params)

    if 'Items' in result:
        if len(result['Items']) == 0:
            print("no jobs finished processing recently. ")
        else:
            for x in result['Items']:
                try:
                    state = sync(x['id'])

                    print("schedule aggregation for {}".format(x))
                    schedule_to_queue({"job": x['id'], "env": x['env'], "profile": x['profile']},
                                      service=SECURE_CARROT_AGGREGATOR)
                    update_job_state(job=x['id'], state=States.AGGREGATION_SCHEDULED)
                except Exception as e:
                    traceback.print_exc()
                    update_job_state(job=x['id'], state=States.FAILED, reason=str(e))
    else:
        print("no jobs finished processing recently. ")
