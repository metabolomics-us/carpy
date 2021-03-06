import simplejson as json
from jsonschema import validate, ValidationError

from stasis.headers import __HTTP_HEADERS__
from stasis.schema import __TRACKING_SCHEMA__
from stasis.tables import save_sample_state


def triggerEvent(data):
    """
        submits the given data to the table (previously queue)

    :param data: requires sample and status in it, to be considered validd
    :return: a serialized version of the submitted message
    """
    try:
        validate(data, __TRACKING_SCHEMA__)
    except ValidationError as e:
        return {
            'body': json.dumps({'error': str(e), 'content': data}),
            'statusCode': 500,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }

    item, saved = save_sample_state(
        sample=data['sample'],
        state=data['status'],
        fileHandle=data.get('fileHandle', None),
        reason=data.get('reason', data.get('failed',None))

    )

    return {
        'body': json.dumps(item),
        'statusCode': saved['ResponseMetadata']['HTTPStatusCode'],
        'isBase64Encoded': False,
        'headers': __HTTP_HEADERS__
    }


def create(event, context):
    """
        creates a new sample tracking object, from a html api request

        :param event:
        :param context:
        :return:
    """
    if 'body' not in event:
        raise Exception("please ensure you provide a valid body")
    data = json.loads(event['body'])

    return triggerEvent(data)
