import json
import os

from jsonschema import validate

from stasis.headers import __HTTP_HEADERS__
from stasis.jobs.states import States
from stasis.schedule.schedule import _get_queue, schedule_to_queue
from stasis.schema import __JOB_SCHEMA__
from stasis.tables import _set_sample_job_state, set_sample_job_state


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

    # store actual job in the job table with state scheduled

    # send to processing queue, might timeout web session for very large jobs
    # refactor later accordingly to let it get processed in a lambda itself to avoid this
    try:
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
        # roll
        raise e


def monitor_jobs(event, context):
    """
    monitors the current jobs in the system. It asks the job table for all unfinished jobs
    if they are ready for processing
    """


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
    arn = _get_queue(client, os.environ["aggregation_queue"])

    serialized = json.dumps(body, use_decimal=True)

    # mark job as currently aggregating

    try:
        # submit item to queue for routing to the correct persistence
        result = client.send_message(
            QueueUrl=arn,
            MessageBody=json.dumps({'default': serialized}),
        )

    except Exception as e:
        # rollback state of this job
        raise e

    return {
        'statusCode': result['ResponseMetadata']['HTTPStatusCode'],
        'headers': __HTTP_HEADERS__,
        'isBase64Encoded': False,
        'body': serialized
    }
