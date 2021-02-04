import time
import traceback

import simplejson as json
from boto3.dynamodb.conditions import Key, Attr
from jsonschema import validate, ValidationError

from stasis.headers import __HTTP_HEADERS__
from stasis.jobs.sync import sync_job
from stasis.schedule.backend import DEFAULT_PROCESSING_BACKEND, Backend
from stasis.schedule.schedule import schedule_to_queue
from stasis.config import SECURE_CARROT_RUNNER
from stasis.schema import __JOB_SCHEMA__, __SAMPLE_JOB_SCHEMA__, __ACQUISITION_SCHEMA__
from stasis.service.Status import *
from stasis.tables import set_sample_job_state, set_job_state, TableManager, update_job_state, \
    get_job_config, get_file_handle, save_sample_state, load_job_samples_with_pagination, _fetch_experiment


def remove_sample_for_job(event, context):
    """
    remove a sample from a stored job
    """

    print(event)
    if 'pathParameters' in event:
        parameters = event['pathParameters']
        if 'sample' in parameters and 'job' in parameters:
            tm = TableManager()
            rid = tm.generate_job_id(parameters['job'], parameters['sample'])
            trktable = tm.get_job_sample_state_table()

            print(f"generated id: {rid}")
            try:
                saved = trktable.delete_item(
                    Key={
                        'id': rid,
                        'job': parameters['job']
                    }
                )  # save or update our item

                print(saved)
                return {

                    'body': '',

                    'statusCode': 200,

                    'isBase64Encoded': False,

                    'headers': __HTTP_HEADERS__

                }
            except Exception as e:

                traceback.print_exc()
                return {

                    'body': str(e),

                    'statusCode': 500,

                    'isBase64Encoded': False,

                    'headers': __HTTP_HEADERS__

                }
        return {
            'statusCode': 503
        }


def store_sample_for_job(event, context):
    """
    stores an associated sample for an job
    :param event:
    :param context:
    :return:
    """

    body = json.loads(event['body'])
    try:
        validate(body, __SAMPLE_JOB_SCHEMA__)
    except ValidationError as e:

        return {

            'body': json.dumps({'state': str(FAILED), 'reason': str(e)}),

            'statusCode': 503,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }
    tracking = body.get('meta', {}).get('tracking', [])
    clazz = body.get('meta', {}).get('class', None)
    sample = body.get('sample')
    job = body.get("job")

    try:
        # overwrite tracking states and extension if it's provided
        for track in tracking:
            if 'extension' in track:
                fileHandle = "{}.{}".format(sample, track['extension'])
            else:
                fileHandle = None

            save_sample_state(sample=sample, state=track['state'], fileHandle=fileHandle)

        if clazz is not None:
            # update the class here by updating the acquisition part
            # 1. get acquisition data
            # 2. set new metadata
            tm = TableManager()
            acqtable = tm.get_acquisition_table()
            result = acqtable.query(
                KeyConditionExpression=Key('id').eq(sample)
            )

            if "Items" in result and len(result['Items']) > 0:
                data = result['Items'][0]
            else:

                timestamp = int(time.time() * 1000)
                data = {
                    'time': timestamp,
                    'id': sample,
                    'sample': sample,
                    'experiment': _fetch_experiment(sample),
                    'acquisition': {
                        'instrument': 'unknown',
                        'ionisation': 'unknown',
                        'method': 'unknown'
                    },
                    'processing': {
                        'method': 'unknown'
                    },
                }

            data['metadata'] = {
                'class': clazz.get('name', 'unknown'),
                'species': clazz.get('species', 'unknown'),
                'organ': clazz.get('organ', 'unknown')
            }
            validate(data, __ACQUISITION_SCHEMA__)
            acqtable.put_item(Item=data)

        set_sample_job_state(
            job=job,
            sample=sample,
            state=SCHEDULING
        )

        return {

            'body': json.dumps(
                {'state': str(SCHEDULING), 'job': job, 'sample': sample, 'reason': 'sample was submitted'}),

            'statusCode': 200,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }
    except Exception as e:
        # update job state in the system to failed with the related reason
        set_sample_job_state(job=job, sample=sample,
                             state=FAILED, reason=str(e))

        traceback.print_exc()
        return {

            'body': json.dumps({'state': str(FAILED), 'job': job, 'sample': sample, 'reason': str(e)}),

            'statusCode': 500,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }


def store_job(event, context):
    """
    stores a job in the internal database
    :param event:
    :param context:
    :return:
    """

    body = json.loads(event['body'])
    try:
        validate(body, __JOB_SCHEMA__)
    except ValidationError as e:

        return {

            'body': json.dumps({'state': str(FAILED), 'reason': str(e)}),

            'statusCode': 503,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }

    job_id = body['id']
    method = body['method']
    profile = body['profile']

    # in case we want to
    tracking = body.get('meta', {}).get('tracking', [])
    if 'resource' in body:
        resource = Backend(body['resource'])
    else:
        resource = DEFAULT_PROCESSING_BACKEND

    # send to processing queue, might timeout web session for very large jobs
    # refactor later accordingly to let it get processed in a lambda itself to avoid this
    try:
        # store actual job in the job table with state scheduled
        set_job_state(job=job_id, method=method, profile=profile,
                      state=body.get('state', ENTERED
                                     ), resource=resource)

        result = get_job_config(job_id)
        return {

            'body': json.dumps({'state': str(result['state']), 'job': job_id}),

            'statusCode': 200,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }
    except Exception as e:
        # update job state in the system to failed with the related reason
        set_job_state(job=job_id, method=method, profile=profile,
                      state=FAILED, reason=str(e))

        traceback.print_exc()
        return {

            'body': json.dumps({'state': str(FAILED), 'job': job_id, 'reason': str(e)}),

            'statusCode': 500,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }


def schedule_job_from_queue(event, context):
    """
    listens to the job queue and executes the scheduling for us.
    :param event:
    :param context:
    :return:
    """

    for message in event['Records']:
        body = json.loads(json.loads(message['body'])['default'])

        if 'job' in body:
            job_id = body['job']
            key = body['key']
            pkey = body.get('paginate', None)

            details = get_job_config(job_id)
            method = details['method']
            profile = details['profile']
            resource = details['resource']

            samples, pkey = load_job_samples_with_pagination(job=job_id, pagination_value=pkey, pagination_size=25)

            schedule_samples_to_queue(job_id, key, method, profile, resource, samples)

            if pkey is None or len(samples) == 0:
                print("job was completely scheduled!")
                set_job_state(job=job_id, method=method, profile=profile,
                              state=SCHEDULED, resource=resource)
            else:
                print('job was too large, requires resubmission to queue to spread the load out!')
                # send job again to queue to
                schedule_to_queue(body={"job": job_id, "key": key, "paginate": pkey},
                                  resource=Backend.NO_BACKEND_REQUIRED, service=None,
                                  queue_name="jobQueue")


def schedule_samples_to_queue(job_id, key, method, profile, resource, samples):
    """
    schedules a sample to the internal scheduling queue for fargate jobs
    """
    for sample in samples:
        try:
            handle = get_file_handle(sample, CONVERTED)
            print("looked up handle {} for sample {}".format(handle, sample))
            schedule_to_queue({
                "sample": handle,
                "method": method,
                "profile": profile,
                "key": key
            }, service=SECURE_CARROT_RUNNER, resource=resource)
            set_sample_job_state(
                job=job_id,
                sample=sample,
                state=SCHEDULED
            )
        except Exception as e:
            set_sample_job_state(
                job=job_id,
                sample=sample,
                state=FAILED,
                reason=str(e)
            )


def schedule_job(event, context):
    """
    schedules the job for our processing
    """

    if 'headers' in event and 'x-api-key' in event['headers']:
        key = event['headers']['x-api-key']
    else:
        key = None

    job_id = event['pathParameters']['job']

    details = get_job_config(job_id)

    if details is None:
        return {

            'body': json.dumps({'error': 'this job has not been stored yet!', 'job': job_id}),

            'statusCode': 404,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }

    if details['state'] == REGISTERING:
        return {

            'body': json.dumps({'error': 'job is currently in state registering and waiting for more samples. It cannot be scheduled yet!', 'job': job_id}),

            'statusCode': 425,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }

    method = details['method']
    profile = details['profile']
    resource = details['resource']
    try:
        # update job state
        set_job_state(job=job_id, method=method, profile=profile,
                      state=SCHEDULING, resource=resource)

        # now send to job sync queue
        schedule_to_queue(body={"job": job_id, "key": key}, resource=Backend.NO_BACKEND_REQUIRED, service=None,
                          queue_name="jobQueue")
        return {

            'body': json.dumps({'state': str(SCHEDULING), 'job': job_id}),

            'statusCode': 200,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }
    except Exception as e:
        # update job state in the system to failed with the related reason
        set_job_state(job=job_id, method=method, profile=profile,
                      state=FAILED, reason=str(e))

        traceback.print_exc()
        return {

            'body': json.dumps({'state': str(FAILED), 'job': job_id, 'reason': str(e)}),

            'statusCode': 500,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }


def monitor_jobs(event, context):
    """
    monitors the current jobs in the system. It asks the job table for all unfinished jobs
    if they are ready for processing

    TODO looks like it's only used in tests and nowhere else
    """

    print("job monitor triggered from event {}".format(event))
    # 1. query JOB state table in state running
    tm = TableManager()
    table = tm.get_job_state_table()

    query_params = {
        'IndexName': 'state-index',
        'Select': 'ALL_ATTRIBUTES',
        'KeyConditionExpression': Key('state').eq(SCHEDULED)
    }

    result = table.query(**query_params)

    if 'Items' in result:
        if len(result['Items']) == 0:
            print("no jobs in state scheduled!")

            query_params = {
                'IndexName': 'state-index',
                'Select': 'ALL_ATTRIBUTES',
                'FilterExpression': Attr('state').ne(SCHEDULED)
            }

            print("WARNING: never good todo a able scan!!! find a better solution")
            result = table.scan(**query_params)
        for x in result['Items']:
            try:

                if x['state'] in [FAILED, AGGREGATED_AND_UPLOADED, AGGREGATING_SCHEDULED, AGGREGATING_SCHEDULING]:
                    continue

                sync_job(x)
            except Exception as e:
                traceback.print_exc()
                update_job_state(job=x['id'], state=FAILED, reason=str(e))
