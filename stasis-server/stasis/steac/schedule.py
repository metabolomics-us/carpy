import json
import traceback
from urllib.parse import unquote

from stasis.config import SECURE_CARROT_STEAC
from stasis.headers import __HTTP_HEADERS__
from stasis.schedule.backend import Backend
from stasis.schedule.schedule import schedule_to_queue
from stasis.service.Status import SCHEDULING, FAILED


def schedule(event, context):
    """
    schedules the job for our processing
    """

    if 'headers' in event and 'x-api-key' in event['headers']:
        key = event['headers']['x-api-key']
    else:
        key = None

    method = unquote(event['pathParameters']['method'])

    try:
        # now send to job sync queue
        schedule_to_queue(body={"method": method, "key": key}, resource=Backend.FARGATE, service=SECURE_CARROT_STEAC,
                          queue_name="schedule_queue")
        return {

            'body': json.dumps({'state': str(SCHEDULING), 'method': method}),

            'statusCode': 200,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }
    except Exception as e:
        traceback.print_exc()
        return {

            'body': json.dumps({'state': str(FAILED), 'method': method, 'reason': str(e)}),

            'statusCode': 500,

            'isBase64Encoded': False,

            'headers': __HTTP_HEADERS__

        }
