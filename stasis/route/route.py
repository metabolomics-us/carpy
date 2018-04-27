import json
import os
import boto3

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
        processes the received metadata and stores it in the internal database
    :param message:
    :return:
    """

    return True


def processTrackingMessage(message):
    """
        sends the received message to the internal database for storage
    :param message:
    :return:
    """

    if 'id' in message:
        table = dynamodb.Table(os.environ['trackingTable'])

        result = table.get_item(
            Key={
                'id': message['id']
            }
        )

        if 'Item' in result:
            # require merge
            data = result['Item']
            message['status'] = data['status'] + message['status']

        # require insert
        result = table.put_item(Item=message)

        print(result)

        return True

    else:
        return False
