import time

import simplejson as json
from boto3.dynamodb.conditions import Key
from jsonschema import validate

from stasis.schema import __TRACKING_SCHEMA__
from stasis.service.Queue import Queue
from stasis.service.Status import Status
from stasis.tables import get_acquisition_table


def triggerEvent(data):
    """
        submits the given data to the queue

    :param data: requires sample and status in it, to be considered validd
    :return: a serialized version of the submitted message
    """
    print("data for event triggering: %s" % data)
    validate(data, __TRACKING_SCHEMA__)

    statusService = Status()
    if not statusService.valid(data['status']):
        raise Exception(
            "please provide the 'status' property in the object")

    # if validation passes, persist the object in the dynamo db

    timestamp = int(time.time() * 1000)

    experiment = _fetch_experiment(data['sample'])

    item = {
        'id': data['sample'],
        'sample': data['sample'],
        'experiment': experiment,
        'status': [
            {
                'time': timestamp,
                'value': data['status'].lower(),
                'priority': statusService.priority(data['status'])
            }
        ]
    }

    if "fileHandle" in data:
        item['status'][-1]['fileHandle'] = data['fileHandle']

    x = Queue()
    return x.submit(item, "tracking")


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


def _fetch_experiment(sample: str) -> str:
    """
        loads the internal experiment id for the given sample
    :param sample:
    :return:
    """
    print("\tfetching experiment id for sample %s" % sample)
    acq_table = get_acquisition_table()

    print("scan result:\n%s" % acq_table.scan())

    result = acq_table.query(
        KeyConditionExpression=Key('id').eq(sample),
        # ---------- or -----------
        #     KeyConditions={
        #         'id': {
        #             'AttributeValueList': [sample],
        #             'ComparisonOperator': 'EQ'
        #         }
        #     },
        ProjectionExpression='experiment'
    )
    print("acq result: %s" % result)

    if result['Items']:
        print(result['Items'])
        item = result['Items'][0]
        if 'experiment' in item:
            print('experiment exists: %s' % item)
            return item['experiment']
        else:
            print('no experiment in item -> unknown')
    else:
        print('no items -> unknown')

    return 'unknown'
