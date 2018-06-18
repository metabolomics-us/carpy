import os

import boto3

db = boto3.resource('dynamodb')


def get_tracking_table():
    """
        provides access to the table and if it doesn't exists
        creates it for us
    :return:
    """

    if 'trackingTable' not in os.environ:
        os.environ['trackingTable'] = "TrackingTable"

    table_name = os.environ['trackingTable']
    existing_tables = boto3.client('dynamodb').list_tables()['TableNames']
    if table_name not in existing_tables:
        try:
            db.create_table(
                TableName=os.environ["trackingTable"],
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'experiment',
                        'KeyType': 'RANGE'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'experiment',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            )
        except Exception as e:
            print("table already exist {}".format(e))

    return db.Table(table_name)


def get_acquisition_table():
    """
        provides access to the table and if it doesn't exists
        creates it for us
    :return:
    """

    if 'acquisitionTable' not in os.environ:
        os.environ['acquisitionTable'] = "AcquisitionTable"

    table_name = os.environ['acquisitionTable']
    existing_tables = boto3.client('dynamodb').list_tables()['TableNames']
    if table_name not in existing_tables:
        try:
            db.create_table(
                TableName=os.environ["acquisitionTable"],
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'experiment',
                        'KeyType': 'RANGE'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'experiment',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            )
        except Exception as e:
            print("table already exist {}".format(e))

    return db.Table(table_name)
