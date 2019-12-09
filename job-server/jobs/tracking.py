import simplejson as json
import time

from boto3.dynamodb.conditions import Key

from jobs.table import TableManager
from jobs.headers import __HTTP_HEADERS__


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
        KeyConditionExpression=Key('id').eq(id)
    )

    if "Items" in result and len(result['Items']) > 0:
        item = result['Items'][0]
        states = result.get('past_states', [])
        states.append(result['state'])
        past_states = list(set(states))
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
