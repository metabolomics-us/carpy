import time

import simplejson as json
from boto3.dynamodb.conditions import Key
from jsonschema import validate

from stasis.schema import __TRACKING_SCHEMA__
from stasis.service.Status import Status
from stasis.tables import TableManager


def triggerEvent(data):
    """
        submits the given data to the table (previously queue)

    :param data: requires sample and status in it, to be considered validd
    :return: a serialized version of the submitted message
    """
    print("data for event triggering: %s" % data)
    validate(data, __TRACKING_SCHEMA__)

    status_service = Status()
    if not status_service.valid(data['status']):
        raise Exception("please provide the 'status' property in the object")

    # if validation passes, persist the object in the dynamo db
    tm = TableManager()

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
                'priority': status_service.priority(data['status'])
            }
        ]
    }

    if "fileHandle" in data:
        item['status'][-1]['fileHandle'] = data['fileHandle']

    item = tm.sanitize_json_for_dynamo(item)

    # put item in table instead of queueing
    table = tm.get_tracking_table()
    saved = table.put_item(
        Item=item,  # save or update our item
        ReturnValues='ALL_NEW'  # return the new values saved on the db
    )
    return saved

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
    tm = TableManager()
    acq_table = tm.get_acquisition_table()

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

    if result['Items']:
        item = result['Items'][0]
        if 'experiment' in item:
            print('experiment exists: %s' % item)
            return item['experiment']
        else:
            print('no experiment in item -> unknown')
    else:
        print('no items -> unknown')

    return 'unknown'
