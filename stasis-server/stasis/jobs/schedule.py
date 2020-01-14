import json
import os
import traceback

from jsonschema import validate

from stasis.headers import __HTTP_HEADERS__
from stasis.jobs.states import States
from stasis.jobs.sync import sync
from stasis.schedule.schedule import _get_queue, schedule_to_queue
from stasis.schema import __JOB_SCHEMA__
from stasis.tables import set_sample_job_state, set_job_state, TableManager, update_job_state


def schedule_job(event, context):
    """
    schedules the job for our processing
    """

    body = json.loads(event['body'])

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
                      state=States.SCHEDULED)
        for sample in samples:
            try:
                schedule_to_queue({
                    "sample": sample,
                    "env": env_,
                    "method": method,
                    "profile": profile,
                    "task_version": task_version
                })
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

    except Exception as e:
        # update job state in the system to failed with the related reason
        set_job_state(job=job_id, method=method, env=env_, profile=profile, task_version=task_version,
                      state=States.FAILED, reason=str(e))
        raise e


def monitor_jobs(event, context):
    """
    monitors the current jobs in the system. It asks the job table for all unfinished jobs
    if they are ready for processing
    """

    # 1. query JOB state table in state running
    tm = TableManager()
    table = tm.get_job_state_table()
    result = table.scan()

    if 'Items' in result:
        for x in result['Items']:
            try:
                state = sync(x['id'])

                if state == States.PROCESSED:
                    schedule_aggregation({"body": json.dumps({"job": x['id']})}, {})
            except Exception as e:
                traceback.print_exc()
                update_job_state(job=x['id'], state=States.FAILED, reason=str(e))


def schedule_aggregation(event, context):
    """
    schedules the actual aggregation. This is only called from a cron based lambda function which monitors
    the queue for us.
    """

    body = json.loads(event['body'])

    # get topic refrence
    import boto3
    client = boto3.client('sqs')

    # if topic exists, we just reuse it
    arn = _get_queue(client, "aggregation_queue")

    serialized = json.dumps(body)

    # mark job as currently aggregating

    try:
        # submit item to queue for routing to the correct persistence
        result = client.send_message(
            QueueUrl=arn,
            MessageBody=json.dumps({'default': serialized}),
        )

        update_job_state(job=body['job'], state=States.AGGREGATION_SCHEDULED)
    except Exception as e:
        # rollback state of this job
        update_job_state(job=body['job'], state=States.FAILED, reason=str(e))
        raise e

    return {
        'statusCode': result['ResponseMetadata']['HTTPStatusCode'],
        'headers': __HTTP_HEADERS__,
        'isBase64Encoded': False,
        'body': serialized
    }
