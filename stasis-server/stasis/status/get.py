import simplejson as json

from stasis.headers import __HTTP_HEADERS__
from stasis.service.Status import States


def get(event, context):
    """
    returns the map of tracking statuses with their priority
    :return:
    """

    return {
        'body': json.dumps(States().states),
        'headers': __HTTP_HEADERS__,
        'statusCode': 200
    }
