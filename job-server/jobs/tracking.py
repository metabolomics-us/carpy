from enum import Enum

import simplejson as json
import time

from boto3.dynamodb.conditions import Key

from jobs.table import TableManager
from jobs.headers import __HTTP_HEADERS__


class States(Enum):
    """
    some standard states
    """

    SCHEDULED = "scheduled",
    PROCESSING = "processing",
    PROCESSED = "processed",
    AGGREGATING = "aggregating",
    AGGREGATED = "aggregated",
    FAILED = "failed",
    DONE = "done"


def create(event, context):
    """
    creates a new tracking record in the dynamodb database
    """
    assert 'body' in event
    body: dict = json.loads(event['body'])

    timestamp = int(time.time() * 1000)

    body['timestamp'] = timestamp
    body['id'] = "{}_{}".format(body['job'], body['sample'])
    tm = TableManager()
    trktable = tm.get_tracking_table()

    result = trktable.query(
        KeyConditionExpression=Key('id').eq(body['id'])
    )

    if body['state'] != States.SCHEDULED.value:
        if "Items" in result and len(result['Items']) > 0:
            item = result['Items'][0]
            states = result.get('past_states', [])
            states.append(item['state'])
            past_states = list(set(states))
        else:
            past_states = []
    else:
        past_states = []

    body['past_states'] = past_states

    body = tm.sanitize_json_for_dynamo(body)
    saved = trktable.put_item(Item=body)  # save or update our item

    saved = saved['ResponseMetadata']

    saved['statusCode'] = saved['HTTPStatusCode']

    return saved


def get(event, context):
    """
    gets the information for the specific record in the dynamodb database
    """

    if 'pathParameters' in event:
        parameters = event['pathParameters']
        if 'sample' in parameters and 'job' in parameters:
            id = "{}_{}".format(parameters['job'], parameters['sample'])
            tm = TableManager()
            table = tm.get_tracking_table()

            result = table.query(
                KeyConditionExpression=Key('id').eq(id)
            )

            if "Items" in result and len(result['Items']) > 0:
                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps(result['Items'][0])
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "no sample found with this identifier : {}".format(
                        event['pathParameters']['sample'])})
                }
        # invalid!
    return {
        'statusCode': 503
    }


def status(event, context):
    """
    returns the status of the current job, as well as some meta information
    """

    if 'pathParameters' in event:
        parameters = event['pathParameters']
        if 'job' in parameters:
            job = parameters['job']
            tm = TableManager()
            table = tm.get_tracking_table()

            query_params = {
                'IndexName': 'job-id-index',
                'Select': 'ALL_ATTRIBUTES',
                'KeyConditionExpression': Key('job').eq(job)
            }
            result = table.query(**query_params
                                 )

            if "Items" in result and len(result['Items']) > 0:

                states = {}
                for x in result['Items']:
                    if x['state'] not in states:
                        states[x['state']] = 0

                    states[x['state']] = states[x['state']] + 1

                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({
                        "count": len(result['Items'
                                     ]),
                        "states": states,
                        "dstate": max(states, key=states.get)
                    }
                    )
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "no job found with this identifier : {}".format(
                        event['pathParameters']['job'])})
                }
        # invalid!
    return {
        'statusCode': 503
    }


def description(event, context):
    """
    returns the complete job description, which can be rather long
    """
    if 'pathParameters' in event:
        parameters = event['pathParameters']
        if 'job' in parameters:
            job = parameters['job']
            tm = TableManager()
            table = tm.get_tracking_table()

            query_params = {
                'IndexName': 'job-id-index',
                'Select': 'ALL_ATTRIBUTES',
                'KeyConditionExpression': Key('job').eq(job)
            }
            result = table.query(**query_params
                                 )

            if "Items" in result and len(result['Items']) > 0:

                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps(
                        result['Items']

                    )
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "no job found with this identifier : {}".format(
                        event['pathParameters']['job'])})
                }
        # invalid!
    return {
        'statusCode': 503
    }


def job_can_aggregate(event, context):
    """
    computes if the given job can be aggregated. Basically the status of all items of the job has to be failed or processed
    for this to be possible
    """


def job_is_done(event, context):
    """
    computes if the given job is done, meaning aggregation is completed and result can be downloaded. The states for all samples has to be
    be failed or aggregated
    """
