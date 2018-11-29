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
        print('running query\nItems: %d' % table.item_count)
        result = table.scan(ProjectionExpression='#m',
                            ExpressionAttributeNames={'#m': 'method'})
        print('MZRT QUERY: %s' % result['Items'])
    except Exception as ex:
        print(ex)
        return {
            "statusCode": 422,
            "headers": __HTTP_HEADERS__,
            "body": json.dumps({"error": str(ex)})
        }

    if 'Items' in result and len(result['Items']) > 0:
        # create a response when sample is found
        mthdList = [x['method'] for x in result['Items']]
        print('items: %s' % mthdList)
        return {
            'statusCode': 200,
            'headers': __HTTP_HEADERS__,
            'body': json.dumps(mthdList)
        }
    else:
        print(result)
        # create a response when sample is not found
        return {
            "statusCode": 404,
            "headers": __HTTP_HEADERS__,
            "body": json.dumps({"error": "method not found"})
        }
