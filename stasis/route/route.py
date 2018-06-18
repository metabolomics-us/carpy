import os

import boto3
import simplejson as json
from boto3.dynamodb.conditions import Key
from stasis.acquisition.create import triggerEvent
from stasis.service.Bucket import Bucket
from stasis.tables import get_acquisition_table, get_tracking_table
from stasis.util.minix_parser import parse_minix_xml

dynamodb = boto3.resource('dynamodb')


def route(events, context):
    """ this routes the incomming messages to the corresponding queues. Main reason is to avoid delays, while processing
    incomming data and events.
    """

    print("received event: " + json.dumps(events, indent=2))

    result = []
    if 'Records' in events:
        if len(events['Records']) > 0:
            for event in events['Records']:
                if 'Sns' in event:
                    if 'Subject' in event['Sns'] and 'Message' in event['Sns']:
                        subject = event['Sns']['Subject'].lower().split(":")
                        message = json.loads(event['Sns']['Message'])

                        if 'route' in subject:
                            if subject[1] == 'tracking':
                                result.append({"event": "tracking", "success": processTrackingMessage(message)})
                            elif subject[1] == 'metadata':
                                result.append({"event": "metadata", "success": processMetaDataMessage(message)})
                            elif subject[1] == 'result':
                                result.append({"event": "result", "success": processResultMessage(message)})
                            else:
                                print("unknown event specified: ", subject[1])
                                result.append({"event": subject[1], "success": False})
                        else:
                            print("routing was not specified in subject!")
                    else:
                        print("subject not provided")
                else:
                    print("no Sns subject in event")
        else:
            print("no records provided in event")
    else:
        print("record is empty!")

    return result


def processMetaDataMessage(message):
    """
        sends the received message to the internal database for storage
    :param message:
    :return:
    """
    table = get_acquisition_table()

    if 'minix' in message and 'url' in message:
        print("handling minix data: " + json.dumps(message, indent=2))
        for x in parse_minix_xml(message['url']):
            # rederict to the appropriate functions
            triggerEvent(x)

        print("finished import")
        return True

    elif 'id' in message and 'minix' not in message:

        if 'experiment' not in message:
            print("user should provide a valid experiment!")
            message['experiment'] = "unknown"

        result = json.dumps(message, use_decimal=True)
        result = json.loads(result, use_decimal=True)

        print("submitting: {}".format(result))
        # require insert
        table.put_item(Item=result)

        return True

    else:
        return False


def processTrackingMessage(message):
    """
        processes the received metadata and stores it in the internal database
    :param message:
    :return:
    """
    print("tracking message: %s" % message)

    if 'id' in message:
        table = get_tracking_table()

        result = table.query(
            KeyConditionExpression=Key('id').eq(message['id'])
        )

        # print(result)
        if 'Items' in result and len(result['Items']) > 0:
            result = result['Items'][0]
            # only keep elements with a lower priority
            result['status'] = [x for x in result['status'] if x['priority'] < message['status'][0]['priority']]
            result['status'] = result['status'] + message['status']
        else:
            result = message

        result['experiment'] = _fetch_experiment(message['id'])

        result = json.dumps(result, use_decimal=True)
        result = json.loads(result, use_decimal=True)

        # print("submitting: {}".format(result))
        # require insert
        result = table.put_item(Item=result)
        # print("result: {}".format(result))

    return True


def _fetch_experiment(sample: str) -> str:
    """
        loads the internal experiment id for the given sample
    :param sample:
    :return:
    """

    table = get_tracking_table()

    result = table.query(
        KeyConditionExpression=Key('id').eq(sample)
    )

    print("query result was {}".format(result))

    if 'Items' in result and len(result['Items']) > 0:
        result = result['Items'][0]
        if 'experiment' in result:
            return result['experiment']
        else:
            "unknown"
    else:
        return "unknown"


def processResultMessage(message):
    """
        processes the received metadata and stores it in the internal database
    :param message:
    :return:
    """

    print(message)

    if 'sample' in message:
        table = Bucket(os.environ['resultTable'])

        existing = table.exists(message['id'])

        if existing:
            existing = json.loads(table.load(message['id']))
            # need to append result to injections
            message['injections'] = {**message['injections'], **existing['injections']}

        print(table.save(message['id'], json.dumps(message)))

        return True

    else:
        print('no id provided')
        return False
