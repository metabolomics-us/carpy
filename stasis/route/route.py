import simplejson as json
import os
import boto3
from stasis.service.Persistence import Persistence
from stasis.util.minix_parser import parse_minix_xml
from stasis.acquisition.create import triggerEvent

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
    table = Persistence(os.environ['acquisitionTable'])

    if 'minix' in message and 'url' in message:
        print("handling minix data: " + json.dumps(message, indent=2))
        for x in parse_minix_xml(message['url']):
            # rederict to the appropriate functions
            triggerEvent(x)

        print("finished import")
        return True

    elif 'id' in message and 'minix' not in message:

        table.save(message)

        return True

    else:
        return False


def processTrackingMessage(message):
    """
        processes the received metadata and stores it in the internal database
    :param message:
    :return:
    """

    if 'id' in message:
        table = Persistence(os.environ['trackingTable'])

        result = table.load(message['id'])

        if result is not None:
            # only keep elements with a lower priority
            result['status'] = [x for x in result['status'] if x['priority'] < message['status'][0]['priority']]
            message['status'] = result['status'] + message['status']

        # req   uire insert
        result = table.save(message)

        return True

    else:
        return False


def processResultMessage(message):
    """
        processes the received metadata and stores it in the internal database
    :param message:
    :return:
    """

    if 'sample' in message:
        table = Persistence(os.environ['resultTable'])

        existing = table.load(message['id'])

        if existing is not None:

            # need to append result to injections
            message['injections'] = {**message['injections'], **existing['injections']}

        table.save(message)

        return True

    else:
        print('no id provided')
        return False
