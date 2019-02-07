import os

import boto3
import simplejson as json
from boto.dynamodb2.exceptions import ResourceInUseException


class TableManager:

    def __init__(self):
        self.db = boto3.resource('dynamodb', 'us-west-2')

    def get_tracking_table(self):
        """
            provides access to the table and if it doesn't exists
            creates it for us
        :return:
        """

        table_name = os.environ['trackingTable']
        existing_tables = boto3.client('dynamodb').list_tables()['TableNames']

        if table_name not in existing_tables:
            try:
                print(self.db.create_table(
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
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 5
                    },
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'experiment-id-index',
                            'KeySchema': [
                                {
                                    'AttributeName': 'experiment',
                                    'KeyType': 'HASH'
                                },
                                {
                                    'AttributeName': 'id',
                                    'KeyType': 'RANGE'
                                }
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 10,
                                'WriteCapacityUnits': 5
                            }
                        }
                    ]
                ))
            except ResourceInUseException as e:
                print("table already exist, ignoring error {}".format(e))
                pass
            except Exception as ex:
                print("table already exist, ignoring error {}".format(ex))
                pass

        return self.db.Table(table_name)

    def get_acquisition_table(self):
        """
            provides access to the table and if it doesn't exists
            creates it for us
        :return:
        """
        table_name = os.environ['acquisitionTable']
        existing_tables = boto3.client('dynamodb').list_tables()['TableNames']
        if table_name not in existing_tables:
            try:
                print(self.db.create_table(
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
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 5
                    },
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'experiment-id-index',
                            'KeySchema': [
                                {
                                    'AttributeName': 'experiment',
                                    'KeyType': 'HASH'
                                },
                                {
                                    'AttributeName': 'id',
                                    'KeyType': 'RANGE'
                                }
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 10,
                                'WriteCapacityUnits': 5
                            }
                        }
                    ])
                )
            except ResourceInUseException as e:
                print("table already exist, ignoring error {}".format(e))
                pass
            except Exception as ex:
                print("table already exist, ignoring error {}".format(ex))
                pass

        return self.db.Table(table_name)

    def get_target_table(self):
        """
            provides access to the table and if it doesn't exists
            creates it for us
        :return:
        """
        table_name = os.environ['targetTable']
        existing_tables = boto3.client('dynamodb').list_tables()['TableNames']

        if table_name not in existing_tables:
            try:
                self.db.create_table(
                    TableName=os.environ["targetTable"],
                    KeySchema=[
                        {
                            'AttributeName': 'method',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'mz_rt',
                            'KeyType': 'RANGE'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'method',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'mz_rt',
                            'AttributeType': 'S'
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 2,
                        'WriteCapacityUnits': 2
                    }
                )
            except ResourceInUseException as e:
                print("table already exist, ignoring error {}".format(e))
                pass
            except Exception as ex:
                print("error %s" % str(ex))
                raise

        return self.db.Table(table_name)

    def sanitize_json_for_dynamo(self, result):
        """
        sanitizes a list and makes it dynamo db compatible
        :param result:
        :return:
        """

        from boltons.iterutils import remap

        result = remap(result,
                       visit=lambda path, key, value: True if isinstance(value, (int, float, complex)) else bool(value))
        data_str = json.dumps(result, use_decimal=True)
        new_result = json.loads(data_str, use_decimal=True)

        return new_result
