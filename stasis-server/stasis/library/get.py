import simplejson as json

from stasis.headers import __HTTP_HEADERS__
from stasis.tables import TableManager


def get(events, context):
    """returns a list of targets for a specific method and if present an MZ_RT value"""
    print("received event: " + json.dumps(events, indent=2))

    tm = TableManager()
    table = tm.get_target_table()

    result = {}
    try:
        result = table.scan(ProjectionExpression='#m',
                            ExpressionAttributeNames={'#m': 'method'})
    except Exception as ex:
        print(ex)
        return {
            "statusCode": 422,
            "headers": __HTTP_HEADERS__,
            "body": json.dumps({"error": str(ex)})
        }

    if 'Items' in result and len(result['Items']) > 0:
        # create a response when sample is found
        mthdList = list(set([x['method'] for x in result['Items']]))
        return {
            'statusCode': 200,
            'headers': __HTTP_HEADERS__,
            'body': json.dumps(mthdList)
        }
    else:
        # create a response when sample is not found
        return {
            "statusCode": 404,
            "headers": __HTTP_HEADERS__,
            "body": json.dumps({"error": "no libraries/methods found"})
        }
