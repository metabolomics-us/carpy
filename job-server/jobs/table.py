import os

import boto3
import simplejson as json
from boto.dynamodb2.exceptions import ResourceInUseException, ValidationException


class TableManager:

    def __init__(self):
        self.db = boto3.resource('dynamodb', 'us-west-2')

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
                            'AttributeName': 'job',
                            'KeyType': 'RANGE'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'id',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'job',
                            'AttributeType': 'S'
                        },

                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 5
                    },
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'job-id-index',
                            'KeySchema': [
                                {
                                    'AttributeName': 'job',
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
            except ValidationException as ex:
                raise ex
            except Exception as ex:
                print("table already exist, ignoring error {}".format(ex))
                pass

        return self.db.Table(table_name)
