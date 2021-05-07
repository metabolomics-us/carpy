import json

from requests import request

from stasis.headers import __HTTP_HEADERS__


def get(events, context):
    """
    load minix data from the remote system
    """
    if 'pathParameters' in events:
        if 'id' in events['pathParameters']:
            minix_id = events['pathParameters']['id']
            url = f"http://minix.fiehnlab.ucdavis.edu/rest/export/{minix_id}"
            print(f"fetching url: {url}")
            result = request(url=url, method="GET")
            return {
                "statusCode": 200,
                "body": result.content
            }
    return {
        "statusCode": 500,
        "headers": __HTTP_HEADERS__,
        "body": json.dumps({"error": "please provide a minix 'id'"})
    }
