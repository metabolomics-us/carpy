from urllib.parse import unquote

import simplejson as json

from stasis.headers import __HTTP_HEADERS__
from stasis.tables import TableManager


def delete(event, context):
    """
        deletes a target from the table

        :param event:
        :param context:
        :return: a serialized version of the submitted message
    """
    # print("received event: " + json.dumps(event, indent=2))

    if 'pathParameters' in event:
        params = event['pathParameters']

        if not params.get('method') or not params.get('mz_rt'):
            return {
                'body': json.dumps({'error': 'missing method and/or mz_rt parameters, please provide both in the url'}),
                'statusCode': 422,
                'headers': __HTTP_HEADERS__
            }

        tm = TableManager()
        table = tm.get_target_table()
        saved = {}
        method = unquote(params.get('method'))
        mz_rt = params.get('mz_rt')

        try:
            saved = table.delete_item(Key={'method': method,
                                           'mz_rt': mz_rt},
                                      ReturnValues='ALL_OLD')
            print('deleted %s -- %s' % (method, mz_rt))
            saved['ResponseMetadata']['HTTPStatusCode'] = 204
            body = {}
        except Exception as e:
            print("ERROR: Could not delete; %s" % str(e))
            saved['ResponseMetadata']['HTTPStatusCode'] = 422
            body = {'error': str(e)}

        return {
            'statusCode': saved['ResponseMetadata']['HTTPStatusCode'],
            'headers': __HTTP_HEADERS__,
            'body': json.dumps(body)
        }
    else:
        return {
            'body': json.dumps({'error': 'invalid request'}),
            'statusCode': 404,
            'headers': __HTTP_HEADERS__
        }
